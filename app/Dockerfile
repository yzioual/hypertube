# ==========================================
# STAGE 1: Build libtorrent & Python Bindings
# ==========================================
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive 
ENV TZ=Europe/Paris

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    build-essential \
    pkg-config \
    git \
    zlib1g-dev \
    libicu-dev \
    libssl-dev \
    python3 \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Download and bootstrap Boost from the official archive mirror
ARG BOOST_VERSION=1.75.0
RUN BOOST_UNDERSCORE=$(echo ${BOOST_VERSION} | tr '.' '_') && \
    curl -sL "https://archives.boost.io/release/${BOOST_VERSION}/source/boost_${BOOST_UNDERSCORE}.tar.gz" > boost.tar.gz && \
    tar -xf boost.tar.gz && \
    mv boost_${BOOST_UNDERSCORE} boost_src

ENV BOOST_ROOT=/build/boost_src
# This variable tells b2 exactly where its internal build framework engine is located
ENV BOOST_BUILD_PATH=${BOOST_ROOT}/tools/build

RUN cd ${BOOST_ROOT} && ./bootstrap.sh

# Clone libtorrent (RC_1_2 branch)
RUN git clone --single-branch --branch RC_1_2 --shallow-submodules --recurse-submodules --depth 1 https://github.com/arvidn/libtorrent.git

# Configure b2 build jam and compile Python Bindings
RUN PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')") && \
    # Write configuration profile mapping compilers and python bindings
    echo "using gcc : : : <cflags>-march=native -std=c++17 <cxxflags>-march=native -std=c++17 ;\nusing python : ${PYTHON_VERSION} : /usr/bin/python${PYTHON_VERSION} : /usr/include/python${PYTHON_VERSION} : /usr/lib/python${PYTHON_VERSION} ;" > /root/user-config.jam && \
    \
    # Build libtorrent C++ core (including the explicit boost path mapping)
    cd /build/libtorrent && \
    ${BOOST_ROOT}/b2 -j$(nproc) --search-id=${BOOST_ROOT} optimization=speed crypto=openssl cxxstd=17 variant=release threading=multi link=static boost-link=static include=${BOOST_ROOT} install --prefix=/usr/local && \
    \
    # Build and stage the Python binding module
    cd /build/libtorrent/bindings/python && \
    ${BOOST_ROOT}/b2 -j$(nproc) --search-id=${BOOST_ROOT} fpic=on optimization=speed crypto=openssl cxxstd=17 variant=release threading=multi libtorrent-link=static boost-link=static include=${BOOST_ROOT} stage_module

# Locate and extract the compiled binary module
RUN mkdir -p /build/dist && \
    find /build/libtorrent/bindings/python -name "libtorrent*.so" -exec cp {} /build/dist/libtorrent.so \;


# ==========================================
# STAGE 2: Lightweight Runtime Environment
# ==========================================
FROM ubuntu:22.04 AS runner

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Safely identify the path dynamically and place the library file
RUN PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')") && \
    mkdir -p /usr/local/lib/python${PYTHON_VERSION}/dist-packages/
COPY --from=builder /build/dist/libtorrent.so /usr/local/lib/python3.10/dist-packages/libtorrent.so

COPY . /app/

COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "flask", "--app", "src/main", "run", "--debug", "--host=0.0.0.0", "--port=8000"]
