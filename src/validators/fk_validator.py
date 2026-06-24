class FkValidator:
    def validate(self, values, target_values) -> bool:
        return set(values).issubset(set(target_values))

