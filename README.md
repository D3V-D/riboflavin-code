# commands
'''docker run --gpus all -it --rm -v "${PWD}:/workspace" -p 8888:8888 --shm-size=16g --name ribo_training nvcr.io/nvidia/pytorch:26.04-py3'''

then
''jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root''

