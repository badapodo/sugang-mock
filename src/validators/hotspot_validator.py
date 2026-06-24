class HotspotValidator:
    def validate(self, actual_ratio: float, expected_ratio: float, tolerance: float = 0.02) -> bool:
        return abs(actual_ratio - expected_ratio) <= tolerance

