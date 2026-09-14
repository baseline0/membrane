# Build CEC2017 benchmark library in isolated reproducible environment
FROM gcc:12-bookworm

WORKDIR /build

# Copy CEC2017 source from sibling repo (build context is baseline0/)
COPY CEC2017-BoundContrained/codes /cec2017_src

# Compile CEC2017 C++ source to shared library
# Remove Windows-specific headers, compile test function only
# Allow undefined symbols (globals defined at call time)
RUN cd /cec2017_src/C\ version && \
    sed -i '/#include.*WINDOWS/d' cec17_test_func.cpp && \
    g++ -shared -fPIC -O3 -lm \
    -Wl,--allow-shlib-undefined \
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
