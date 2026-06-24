from scripts.generate_charts import generate_charts


class ChartExporter:
    """Pipeline adapter for the CSV-driven standalone chart generator."""

    def export(self, context, analysis=None):
        return generate_charts(context.output_dir, context.scenario)
