#!/bin/bash

# Knowledge Platform - Docker Image Build and Push Script
# 知识管理平台 - Docker 镜像构建和推送脚本

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 设置版本号
VERSION=${1:-latest}
REGISTRY="ghcr.io/jackchen1941"

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  Knowledge Platform - Build & Push Docker Images      ║${NC}"
echo -e "${MAGENTA}║  知识管理平台 - 构建和推送 Docker 镜像                  ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Version:${NC}  ${GREEN}${VERSION}${NC}"
echo -e "${BLUE}Registry:${NC} ${GREEN}${REGISTRY}${NC}"
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

# ============================================
# 构建阶段
# ============================================
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  STEP 1: Building Images                               ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

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

# 显示镜像大小
echo -e "${BLUE}📊 Image Sizes:${NC}"
docker images | grep knowledge-platform | grep -E "${VERSION}|latest"
echo ""

# ============================================
# 推送阶段
# ============================================
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  STEP 2: Pushing Images                                ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
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

# ============================================
# 完成
# ============================================
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  ✅ Build and Push Completed Successfully!             ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📦 Images available at:${NC}"
echo ""
echo -e "${GREEN}  Backend:${NC}"
echo "    docker pull ${REGISTRY}/knowledge-platform-backend:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "    docker pull ${REGISTRY}/knowledge-platform-backend:latest"
fi
echo ""
echo -e "${GREEN}  Frontend:${NC}"
echo "    docker pull ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "    docker pull ${REGISTRY}/knowledge-platform-frontend:latest"
fi
echo ""

echo -e "${BLUE}🔗 View packages at:${NC}"
echo "   https://github.com/jackchen1941?tab=packages"
echo ""

echo -e "${YELLOW}📝 Next steps:${NC}"
echo ""
echo "  1. Make images public (if needed):"
echo "     • Visit: https://github.com/jackchen1941?tab=packages"
echo "     • Select package → Settings → Change visibility to 'Public'"
echo ""
echo "  2. Test pulling images:"
echo "     docker pull ${REGISTRY}/knowledge-platform-backend:${VERSION}"
echo "     docker pull ${REGISTRY}/knowledge-platform-frontend:${VERSION}"
echo ""
echo "  3. Deploy using Docker Compose:"
echo "     docker-compose -f docker-compose.ghcr.yml up -d"
echo ""
echo "  4. Or deploy to Kubernetes:"
echo "     kubectl apply -f deployment/kubernetes/"
echo ""

echo -e "${GREEN}🎉 All done! Your images are ready for deployment!${NC}"
