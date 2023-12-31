FROM khulnasoft/aikit:latest

# Install Aikit
RUN rm -rf aikit && \
    git clone https://github.com/khulnasoft/aikit && \
    cd aikit && \
    cat requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    cat optional.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    python3 -m pip install --user -e .

# Install Aikit Mech
RUN git clone https://github.com/khulnasoft/mech && \
    cd mech && \
    cat requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    cat optional.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    python3 -m pip install --user -e .

# Install Aikit Vision
RUN git clone https://github.com/khulnasoft/vision && \
    cd vision && \
    cat requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    cat optional.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    python3 -m pip install --user -e .

# Install Aikit Robot
RUN git clone https://github.com/khulnasoft/robot && \
    cd robot && \
    cat requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    cat optional.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    python3 -m pip install --user -e .

# Install Aikit Demo Utils
RUN git clone https://github.com/khulnasoft/demo-utils && \
    cd demo-utils && \
    cat requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin && \
    python3 -m pip install --user -e .

COPY requirements.txt /
RUN cat requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin

COPY aikit_robot_demos/requirements.txt /demo_requirements.txt
RUN cat demo_requirements.txt | grep -v "aikit-" | pip3 install --no-cache-dir -r /dev/stdin

# RUN python3 test_dependencies.py -fp requirements.txt,demo_requirements.txt && \
#     rm -rf requirements.txt && \
#     rm -rf demo_requirements.txt

WORKDIR /robot