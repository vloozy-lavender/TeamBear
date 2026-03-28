import logging
from src.core.api_client import RoostooClient

logging.basicConfig(level=logging.DEBUG)

print("Testing all signature versions...")
print("=" * 60)

for version in [1, 2, 3]:
    print(f"\n🔑 Testing Signature Version {version}...")
    try:
        client = RoostooClient(signature_version=version)
        balance = client.get_balance()
        print(f"✅ SUCCESS with v{version}!")
        print(f"   Balance: {balance}")
        break
    except Exception as e:
        print(f"❌ Failed v{version}: {e}")

print("=" * 60)
