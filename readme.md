#Conda cmds

conda create -n myenv2 python=3.11
conda activate myenv2

conda env list
conda info --envs
echo $CONDA_DEFAULT_ENV

conda install -c anaconda pycrypto
conda install -c conda-forge pycryptodome
pip install Flask
pip install flask-cors

pip list
