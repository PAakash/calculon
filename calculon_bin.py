"""
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*  https://www.apache.org/licenses/LICENSE-2.0
*
* See the NOTICE file distributed with this work for additional information
* regarding copyright ownership.
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
"""

import argparse
import logging
import sys

import calculon

if __name__ == "__main__":
    # CLI inspired from: https://github.com/ssnetsim/ssplot/

    # Creates an argparser and subparsers.
    desc = "Calculon: Co-design for large scale parallel applications"
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument(
        "-l", "--log", default="-", help="Sets the log file, or - for stdout (default)"
    )
    ap.add_argument(
        "-v",
        "--verbosity",
        default="INFO",
        help="Sets the logging level (see logging docs)",
    )
    sp = ap.add_subparsers(
        title="commands",
        dest="command",
        description="commands available in Calculon",
        help="the command",
    )
    sp.required = True

    # Registers each command line interface.
    for cls in calculon.CommandLine.command_lines():
        cls.create_parser(sp)

    # Parses the args and creates the logger
    args = ap.parse_args()
    logger = logging.getLogger()
    if args.log == "-":
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    else:
        fd = open(args.log, "w")
        logger.addHandler(logging.StreamHandler(stream=fd))
    logger.setLevel(args.verbosity)

    # Calls the corresponding command function
    sys.exit(args.func(logger, args))
