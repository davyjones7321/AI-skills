"""Quick test for registry API endpoints."""
import urllib.request
import json


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def main():
    base = "http://127.0.0.1:8000"

    # Test 1: Health check
    print("=== Test 1: Health Check ===")
    data = get(f"{base}/health")
    print(data)

    # Test 2: List skills (paginated)
    print("\n=== Test 2: List Skills ===")
    data = get(f"{base}/skills/?page=1&limit=5")
    print(f"Total: {data['total_count']}, Page: {data['page']}, Showing: {len(data['skills'])}")
    for s in data["skills"]:
        print(f"  {s['author']}/{s['id']}@{s['version']} ({s['exec_type']})")

    # Test 3: Search by query
    print("\n=== Test 3: Search by query ===")
    data = get(f"{base}/skills/search?q=sentiment")
    print(f"Results for 'sentiment': {len(data['skills'])}")
    for s in data["skills"]:
        print(f"  {s['id']}")

    # Test 4: Search by type
    print("\n=== Test 4: Search by type=code ===")
    data = get(f"{base}/skills/search?type=code")
    print(f"Code skills: {len(data['skills'])}")
    for s in data["skills"]:
        print(f"  {s['id']}")

    # Test 5: Search by tag
    print("\n=== Test 5: Search by tag=nlp ===")
    data = get(f"{base}/skills/search?tag=nlp")
    print(f"NLP skills: {len(data['skills'])}")
    for s in data["skills"]:
        print(f"  {s['id']}")

    # Test 6: Get skill by author/id
    print("\n=== Test 6: Get specific skill ===")
    data = get(f"{base}/skills/ai-skills-team/summarize-document")
    print(f"Got: {data['author']}/{data['id']}@{data['version']}")
    print(f"YAML length: {len(data['yaml_content'])} chars")

    # Test 7: Auth
    print("\n=== Test 7: Auth /auth/me ===")
    data = get(f"{base}/auth/me", headers={"Authorization": "Bearer dev-token-aiskills"})
    print(data)

    print("\n=== All API tests PASSED ===")


if __name__ == "__main__":
    main()
