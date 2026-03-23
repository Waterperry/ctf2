while true; do
    mkdir /root/project;
    cd /root/project;
    uv init;
    cat /root/pyproject_postfix.txt >> ./pyproject.toml
    sleep 5;
    uv add numpy --verbose;
    uv run main.py;
    cd /root;
    rm -rf /root/project;
    sleep 60;
done
