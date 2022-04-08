set -e
cd "${0%/*}"

if [ -d "env/" ]
then
    echo "Directory env/ already exists."
    exit 1
fi

python3 -m venv env
source env/bin/activate

pip install wheel
pip install -r src/requirements.txt
