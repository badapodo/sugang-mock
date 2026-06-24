#!/usr/bin/env python3
import argparse
from pathlib import Path

from src.core.config_loader import load_scenario, load_schema_map
from src.core.context import Context
from src.core.pipeline import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Generate and validate enrollment performance-test data")
    parser.add_argument("--scenario", default="config/scenario.yaml", help="scenario YAML path")
    parser.add_argument("--schema", default="config/schema-map.yaml", help="schema-map YAML path")
    parser.add_argument("--seed", type=int, help="override scenario seed")
    parser.add_argument("--output", default="output", help="output directory")
    return parser.parse_args()


def main():
    args = parse_args()
    scenario = load_scenario(args.scenario)
    schema = load_schema_map(args.schema)
    seed = args.seed if args.seed is not None else scenario.get("seed", 42)
    context = Context(scenario, schema, seed, Path(args.output))
    Pipeline().run(context)


if __name__ == "__main__":
    main()

