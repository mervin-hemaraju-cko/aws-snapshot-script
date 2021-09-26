# This is only a run file that will trigger the main function
# with a test case
# This file is not needed in production
import sys
from main import main

if __name__ == "__main__":
    main(sys.argv[1:])