import argparse
import sys, os

from src.LCAutomate.common_simplified import DEFAULT_IMPACT_ASSESSMENT_METHOD, DEFAULT_NUMBER_OF_ITERATIONS, CalculationTypeNames
from src.olca__patched import ipc as olca

from src.LCAutomate.model.model import Model
from src.LCAutomate.process_hierarchy.process_hierarchy import ProcessHierarchy
from src.LCAutomate.calculation.calculation import Calculation
from src.LCAutomate.product_system.product_system import ProductSystem


def main():
    parser = argparse.ArgumentParser(prog="LCAutomate")

    # TODO: Need 2 earlier steps:
    #       1. Create a kind of template file for each of the replicated processes with the key columns plus a tag column
    #       2. Merge the template file with the actual data file which also has a tag column

    parser.add_argument("operation", type=str, 
                        choices=["model", "process-hierarchy", "product-system", "calculation"],
                        help="Perform the chosen LCAutomate operation")
    parser.add_argument("-i", "--input-root-folder", type=str,
                        help="Root folder for automation")
    parser.add_argument("-r", "--restart", action="store_true", default=False,
                        help="Restart this operation, ignoring previous state (default False)")
    parser.add_argument("-c", "--calculation-type", type=str,
                        choices=CalculationTypeNames.list(), default=CalculationTypeNames.UPSTREAM_ANALYSIS,
                        help=f"Calculation type for the calculation operation (default '{CalculationTypeNames.UPSTREAM_ANALYSIS}')")
    parser.add_argument("-im", "--impact-assessment-method", type=str, default=DEFAULT_IMPACT_ASSESSMENT_METHOD,
                        help=f"Impact assessment method for the calculation operation (default '{DEFAULT_IMPACT_ASSESSMENT_METHOD}')")
    parser.add_argument("-n", "--number-of-iterations", type=int, default=DEFAULT_NUMBER_OF_ITERATIONS,
                        help=f"Number of iterations for Monte Carlo simulation (default {DEFAULT_NUMBER_OF_ITERATIONS}) (ignored for other calculation types)")

    # This is required to do pre-parsing of the arguments because argparse can't handle an argument value containing spaces!
    keywords = [
        "model", "process-hierarchy", "product-system", "calculation",
        "-i", "--input-root-folder",
        "-r", "--restart",
        "-c", "--calculation-type",
        "-im", "--impact-assessment-method",
        "-n", "--number-of-iterations",
    ]



    # Here is the pre-parsing step mentioned above
    sys_args = sys.argv[1:]
    modified_args = []
    in_impact_assessment_method = False
    impact_assessment_method = ""
    for arg in sys_args:
        if not in_impact_assessment_method:
            modified_args.append(arg)
            if arg == "-im" or arg == "--impact-assessment-method":
                in_impact_assessment_method = True
        else:
            if arg in keywords:
                in_impact_assessment_method = False
                if len(impact_assessment_method) > 0:
                    modified_args.append(impact_assessment_method)
                modified_args.append(arg)
            else:
                impact_assessment_method = f"{impact_assessment_method} {arg}" if len(impact_assessment_method) > 0 else arg

    # Now we can proceed normally
    args = parser.parse_args(args=modified_args)
    print(f"args.operation: {args.operation}")
    if not args.input_root_folder:
        print("ERROR: --input-root-folder must be supplied")
        sys.exit(1)

    if not os.path.isdir(args.input_root_folder):
        print(f"ERROR: --input-root-folder {args.input_root_folder} must be a folder")
        sys.exit(1)

    print(f"args.input_root_folder: {args.input_root_folder}")
    if args.operation == "calculation":
        print(f"args.calculation_type: {args.calculation_type}")
        print(f"args.impact_assessment_method: {args.impact_assessment_method}")
        if args.calculation_type == CalculationTypeNames.MONTE_CARLO_SIMULATION:
            print(f"args.number_of_iterations: {args.number_of_iterations}")

    client = olca.Client(8080)
    if args.operation == "model":
        module = Model(client, args.input_root_folder, args.restart)
    elif args.operation == "process-hierarchy":
        module = ProcessHierarchy(client, args.input_root_folder, args.restart)
    elif args.operation == "product-system":
        module = ProductSystem(client, args.input_root_folder, args.restart)
    elif args.operation == "calculation":
        module = Calculation(
            client, args.input_root_folder, args.restart, 
            args.calculation_type, 
            args.impact_assessment_method, 
            args.number_of_iterations
        )
    else:
        print(f"ERROR: Unrecognized operation: {args.operation}")
        sys.exit(1)

    done = module.do()
    sys.exit(0) if done else sys.exit(1)


if __name__ == '__main__':
    main()
