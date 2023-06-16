SERVICE=${1}
DOCKERFILE=${2}
ECR_REPO=${ECR_URI}/${SERVICE}

docker build -t ${ECR_REPO}:${GITHUB_SHA} --cache-from ${ECR_REPO}:latest -f ${DOCKERFILE} .
docker push ${ECR_REPO}:${GITHUB_SHA}
echo "Image pushed with tag:${GITHUB_SHA}"

curl -H "buddy-api-key:${BUDDY_API_KEY}" -d "area=${APP_ENV}&deployment=${SERVICE}&imageuri=${ECR_REPO}:${GITHUB_SHA}&mode=deploy" -X POST "${DEPLOYER_URL}/api/update_deployment"