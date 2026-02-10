#!/bin/bash

# Knowledge Platform - Docker Image Build Script
# 知识管理平台 - Docker 镜像构建脚本

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 设置版本号
VERSION=${1:-latest}
REGISTRY="ghcr.io/jackchen1941"

echo -e "${BLUE}🚀 Building Knowledge Platform Docker Images${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Version: ${GREEN}${VERSION}${NC}"
echo -e "Registry: ${GREEN}${REGISTRY}${NC}"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker daemon first"
    exit 1
fi

# 构建后端镜像
echo -e "${YELLOW}📦 Building backend image...${NC}"
cd backend
docker build -t ${REGISTRY}/knowledge-platform-backend:${VERSION} .
if [ "$VERSION" != "latest" ]; then
    docker tag ${REGISTRY}/knowledge-platform-backend:${VERSION} ${REGISTRY}/knowledge-platform-backend:latest
    echo -e "${GREEN}✓ Tagged as latest${NC}"
fi
cd ..
echo -e "${GREEN}✓ Backend image built successfully${NC}"
echo ""

# 构建前端镜像
echo -e "${YELLOW}📦 Building frontend image...${NC}"
cd frontend
docker build -t ${REGISTRY}/knowledge-platform-frontend:${VERSION} .
if [ "$VERSION" != "latest" ]; then
    docker tag ${REGISTRY}/knowledge-platform-frontend:${VERSION} ${REGISTRY}/knowledge-platform-frontend:latest
    echo -e "${GREEN}✓ Tagged as latest${NC}"
fi
cd ..
echo -e "${GREEN}✓ Frontend image built successfully${NC}"
echo ""

# 显示构建的镜像
echo -e "${BLUE}📦 Built Images:${NC}"
echo -e "${GREEN}  Backend:${NC}"
echo "    - ${REGISTRY}/knowledge-platform-backend:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "    - ${REGISTRY}/knowledge-platform-backend:latest"
fi
echo -e "${GREEN}  Frontend:${NC}"
echo "    - ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "    - ${REGISTRY}/knowledge-platform-frontend:latest"
fi
echo ""

# 显示镜像大小
echo -e "${BLUE}📊 Image Sizes:${NC}"
docker images | grep knowledge-platform | grep -E "${VERSION}|latest"
echo ""

echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Test images locally:"
echo "     docker-compose up -d"
echo ""
echo "  2. Push to registry:"
echo "     ./push-images.sh ${VERSION}"
echo ""
echo "  3. Or build and push in one step:"
echo "     ./build-and-push.sh ${VERSION}"
