 #!/usr/bin/env bash

echo " "
echo "Setting up LCAutomate..."
echo "========================"
echo " "
WHICH_PYTHON=$(which python)
EXPECTED=$(pwd)"/venv/Scripts/python"
if [ "$WHICH_PYTHON" != "$EXPECTED" ]; then
  echo "Setting up virtual environment..."
  echo " "
  python -m venv venv
  source venv/Scripts/activate
  echo "Virtual environment in place"
  echo " "
fi

WHICH_LCAUTOMATE=$(which LCAutomate)
EXPECTED=$(pwd)"/venv/Scripts/LCAutomate"
if [ "$WHICH_LCAUTOMATE" != "$EXPECTED" ]; then
  echo "Installing LCAutomate (this may take a few minutes)..."
  echo "------------------------------------------------------"
  echo " "
  python -m pip install .
fi
echo "LCAutomate installed"
echo "  - usage instructions follow..."
echo " "
LCAutomate
