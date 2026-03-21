"""
Risk Assessment Module
Calculates collision risk based on proximity, motion, lane, object type,
speed, size, temporal smoothing, time-to-collision, and multi-object interaction.
"""

import math
from config import (
    RISK_WEIGHTS,
    RISK_THRESHOLDS,
    OBJECT_RISK,
    TTC_CRITICAL_SECONDS,
    RISK_SMOOTHING_ALPHA,
    MULTI_OBJECT_BOOST,
    OUTPUT_FPS,
)


class RiskAssessor:
    def __init__(self, frame_height: int = None):
        """Initialize risk assessor."""
        self.frame_height = frame_height
        self.weights = RISK_WEIGHTS
        self.thresholds = RISK_THRESHOLDS
        self.object_risk = OBJECT_RISK
        self.ttc_critical = TTC_CRITICAL_SECONDS
        self.smoothing_alpha = RISK_SMOOTHING_ALPHA
        self.multi_boost = MULTI_OBJECT_BOOST
        self.fps = OUTPUT_FPS

        # Per-object EMA history  {obj_id: smoothed_score}
        self._score_history: dict[int, float] = {}

    def set_frame_height(self, height: int):
        """Set frame height for distance calculations."""
        self.frame_height = height

    # ------------------------------------------------------------------
    # Individual risk factors
    # ------------------------------------------------------------------

    def _distance_risk(self, obj_info: dict) -> float:
        """Objects at the bottom of frame are closer to the camera."""
        if self.frame_height:
            y_bottom = obj_info["bbox"][3]
            return y_bottom / self.frame_height
        return 0.5

    def _motion_risk(self, obj_info: dict) -> float:
        """Score based on whether the object is approaching, departing, etc."""
        motion = obj_info.get("motion", "UNKNOWN")
        return {
            "APPROACHING": 1.0,
            "STATIONARY": 0.5,
            "DEPARTING": 0.1,
        }.get(motion, 0.3)

    def _lane_risk(self, obj_info: dict) -> float:
        """Center lane is highest risk; left/right are moderate."""
        lane = obj_info.get("lane", "UNKNOWN")
        return {
            "CENTER": 1.0,
            "LEFT": 0.5,
            "RIGHT": 0.5,
        }.get(lane, 0.3)

    def _object_type_risk(self, obj_info: dict) -> float:
        """Vulnerable road users (pedestrians, cyclists) score higher."""
        class_name = obj_info.get("class_name", "car")
        return self.object_risk.get(class_name, 0.5)

    def _speed_risk(self, obj_info: dict) -> float:
        """Faster-moving objects are more dangerous (uses velocity vector)."""
        vx, vy = obj_info.get("velocity", (0, 0))
        speed = math.hypot(vx, vy)
        # Normalize: >=20 px/frame is extreme; clamp to [0, 1]
        return min(speed / 20.0, 1.0)

    def _size_risk(self, obj_info: dict) -> float:
        """Larger bounding boxes indicate closer objects."""
        if not self.frame_height:
            return 0.5
        bbox = obj_info["bbox"]
        box_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        # Frame area as reference; bbox occupying >= 25 % of frame ≈ max risk
        frame_area = self.frame_height * (self.frame_height * 16 / 9)  # approx
        ratio = box_area / frame_area if frame_area else 0
        return min(ratio / 0.25, 1.0)

    # ------------------------------------------------------------------
    # Time-to-collision (TTC)
    # ------------------------------------------------------------------

    def _estimate_ttc(self, obj_info: dict) -> float | None:
        """
        Rough TTC from the area growth rate reported by the tracker.

        If area is growing by *r* percent per frame and the object occupies
        fraction *f* of the frame, a simple model gives:
            TTC ≈ (1 - f) / (f * r * fps)

        Returns estimated seconds to collision, or None if not computable.
        """
        area_change = obj_info.get("area_change", None)
        if area_change is None or area_change <= 0:
            return None  # not approaching or no data

        bbox = obj_info["bbox"]
        box_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if not self.frame_height or box_area <= 0:
            return None

        frame_area = self.frame_height * (self.frame_height * 16 / 9)
        f = box_area / frame_area if frame_area else 0
        if f <= 0 or area_change <= 0:
            return None

        try:
            ttc_frames = (1.0 - f) / (f * area_change)
            ttc_seconds = ttc_frames / self.fps if self.fps else ttc_frames / 30
            return max(ttc_seconds, 0.0)
        except ZeroDivisionError:
            return None

    # ------------------------------------------------------------------
    # Core scoring
    # ------------------------------------------------------------------

    def calculate_risk(self, obj_info: dict, obj_id: int = None) -> dict:
        """
        Calculate risk score for a detected object.

        Args:
            obj_info: Detection info with bbox, motion, lane, class_name, velocity
            obj_id:   Object ID (used for temporal smoothing)

        Returns:
            Dict with 'score' (0-1), 'level' (LOW/MEDIUM/HIGH/CRITICAL),
            'factors' breakdown, and optional 'ttc' seconds.
        """
        factors = {
            "distance": self._distance_risk(obj_info),
            "motion": self._motion_risk(obj_info),
            "lane": self._lane_risk(obj_info),
            "object_type": self._object_type_risk(obj_info),
            "speed": self._speed_risk(obj_info),
            "size": self._size_risk(obj_info),
        }

        # Weighted sum
        score = sum(factors[k] * self.weights.get(k, 0) for k in factors)

        # TTC escalation
        ttc = self._estimate_ttc(obj_info)
        if ttc is not None and ttc < self.ttc_critical:
            # Linearly scale boost: 0 s → full boost (0.2), ttc_critical → 0
            boost = 0.2 * (1.0 - ttc / self.ttc_critical)
            score = min(score + boost, 1.0)
            factors["ttc_boost"] = round(boost, 3)

        # Temporal smoothing (EMA)
        if obj_id is not None:
            prev = self._score_history.get(obj_id, score)
            score = self.smoothing_alpha * score + (1 - self.smoothing_alpha) * prev
            self._score_history[obj_id] = score

        # Clamp
        score = max(0.0, min(score, 1.0))

        # Determine risk level
        if score < self.thresholds["low"]:
            level = "LOW"
        elif score < self.thresholds["medium"]:
            level = "MEDIUM"
        elif score < self.thresholds["high"]:
            level = "HIGH"
        else:
            level = "CRITICAL"

        result = {
            "score": round(score, 2),
            "level": level,
            "factors": factors,
        }
        if ttc is not None:
            result["ttc"] = round(ttc, 2)

        return result

    # ------------------------------------------------------------------
    # Batch assessment
    # ------------------------------------------------------------------

    def assess_all(self, tracked_objects: dict) -> dict:
        """
        Calculate risk for all tracked objects, then apply multi-object boost.

        Args:
            tracked_objects: Dict from tracker / lane detector

        Returns:
            Same dict with 'risk' key added to each object
        """
        # Phase 1: individual risk scores
        for obj_id, obj_info in tracked_objects.items():
            obj_info["risk"] = self.calculate_risk(obj_info, obj_id=obj_id)

        # Phase 2: multi-object interaction boost
        self._apply_multi_object_boost(tracked_objects)

        # Prune stale smoothing history
        active_ids = set(tracked_objects.keys())
        stale = [k for k in self._score_history if k not in active_ids]
        for k in stale:
            del self._score_history[k]

        return tracked_objects

    def _apply_multi_object_boost(self, tracked_objects: dict):
        """
        If multiple objects are approaching in the CENTER lane at the same time,
        boost all their risk scores because the driver has fewer escape routes.
        """
        center_approaching = [
            obj_id
            for obj_id, info in tracked_objects.items()
            if info.get("lane") == "CENTER"
            and info.get("motion") == "APPROACHING"
        ]

        if len(center_approaching) >= 2:
            for obj_id in center_approaching:
                risk = tracked_objects[obj_id]["risk"]
                boosted = min(risk["score"] + self.multi_boost, 1.0)
                risk["score"] = round(boosted, 2)
                risk["factors"]["multi_object_boost"] = self.multi_boost

                # Re-evaluate level after boost
                if boosted < self.thresholds["low"]:
                    risk["level"] = "LOW"
                elif boosted < self.thresholds["medium"]:
                    risk["level"] = "MEDIUM"
                elif boosted < self.thresholds["high"]:
                    risk["level"] = "HIGH"
                else:
                    risk["level"] = "CRITICAL"
