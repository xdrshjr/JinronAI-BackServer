export HF_HOME=/mnt/mydisk/models;
export https_proxy=http://127.0.0.1:7897;
export http_proxy=http://127.0.0.1:7897;
export all_proxy=socks5://127.0.0.1:7897;

#export CUDA_VISIBLE_DEVICES=1
python 03_run_with_lora.py