sudo apt update
sudo apt install python3-pip
alias python=python3
sudo make install
sudo python3 -m uvicorn app:app --port 80
