FROM quay.io/synthai/institute

RUN pip install tox

# Upload our actual code
WORKDIR /usr/local/institute/
COPY . ./

# Run tox. Keep printing so Travis knows we're alive.
CMD ["bash", "-c", "( while true; do echo '.'; sleep 60; done ) & tox"]
