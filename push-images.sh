#!/bin/bash

# Knowledge Platform - Docker Image Push Script
# 知识管理平台 - Docker 镜像推送脚本

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

echo -e "${BLUE}🚀 Pushing Knowledge Platform Docker Images${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Version: ${GREEN}${VERSION}${NC}"
echo -e "Registry: ${GREEN}${REGISTRY}${NC}"
echo ""

# 检查是否已登录
echo -e "${YELLOW}🔐 Checking Docker registry login...${NC}"
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo -e "${RED}❌ Not logged in to Docker registry${NC}"
    echo ""
    echo "Please login first:"
    echo "  docker login ghcr.io -u jackchen1941"
    echo ""
    echo "You will need a GitHub Personal Access Token with 'write:packages' permission"
    echo "Create one at: https://github.com/settings/tokens"
    exit 1
fi
echo -e "${GREEN}✓ Logged in to Docker registry${NC}"
echo ""

# 检查镜像是否存在
echo -e "${YELLOW}🔍 Checking if images exist...${NC}"
if ! docker images | grep -q "${REGISTRY}/knowledge-platform-backend.*${VERSION}"; then
    echo -e "${RED}❌ Backend image not found: ${REGISTRY}/knowledge-platform-backend:${VERSION}${NC}"
    echo "Please build the image first: ./build-images.sh ${VERSION}"
    exit 1
fi
if ! docker images | grep -q "${REGISTRY}/knowledge-platform-frontend.*${VERSION}"; then
    echo -e "${RED}❌ Frontend image not found: ${REGISTRY}/knowledge-platform-frontend:${VERSION}${NC}"
    echo "Please build the image first: ./build-images.sh ${VERSION}"
    exit 1
fi
echo -e "${GREEN}✓ Images found${NC}"
echo ""

# 推送后端镜像
echo -e "${YELLOW}📤 Pushing backend image...${NC}"
docker push ${REGISTRY}/knowledge-platform-backend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${REGISTRY}/knowledge-platform-backend:latest
fi
echo -e "${GREEN}✓ Backend image pushed successfully${NC}"
echo ""

# 推送前端镜像
echo -e "${YELLOW}📤 Pushing frontend image...${NC}"
docker push ${REGISTRY}/knowledge-platform-frontend:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker push ${REGISTRY}/knowledge-platform-frontend:latest
fi
echo -e "${GREEN}✓ Frontend image pushed successfully${NC}"
echo ""

echo -e "${GREEN}✅ Push completed successfully!${NC}"
echo ""
echo -e "${BLUE}📦 Images available at:${NC}"
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
echo -e "${BLUE}🔗 View packages at:${NC}"
echo "   https://github.com/jackchen1941?tab=packages"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Make images public (if needed):"
echo "     Visit package settings and change visibility to 'Public'"
echo ""
echo "  2. Test pulling images:"
echo "     docker pull ${REGISTRY}/knowledge-platform-backend:${VERSION}"
echo "     docker pull ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
echo ""
echo "  3. Deploy using images:"
echo "     docker-compose -f docker-compose.ghcr.yml up -d"
