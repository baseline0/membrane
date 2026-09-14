# Build CEC2017 benchmark library in isolated reproducible environment
FROM gcc:12-bookworm

WORKDIR /build

# Copy CEC2017 source from sibling repo
COPY ../CEC2017-BoundConstrained/codes /cec2017_src

# Compile CEC2017 C++ source to shared library
RUN cd /cec2017_src/C\ version && \
    gcc -shared -fPIC -O3 -lm \
    -Wno-all \
    cec17_test_func.cpp \
    -o /build/libcec2017.so && \
    chmod 755 /build/libcec2017.so && \
    ls -lh /build/libcec2017.so

# Copy input data (rotation/shift matrices) for runtime
RUN cp -r /cec2017_src/C\ version/input_data /build/

# Output stage: library ready for ctypes binding
VOLUME /output
CMD cp /build/libcec2017.so /output/ && \
    cp -r /build/input_data /output/ && \
    echo "✓ CEC2017 library built and output to /output"
