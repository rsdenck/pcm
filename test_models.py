#!/usr/bin/env python3
"""
Simple test script to validate the backup models can be imported correctly.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the base and models directly without going through pcm.core
    from pcm.core.database.base import Base
    from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
    from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
    
    print("✓ Successfully imported backup models")
    
    # Test enum values
    print(f"✓ ServerStatus values: {list(ServerStatus)}")
    print(f"✓ DatastoreStatus values: {list(DatastoreStatus)}")
    
    # Test model attributes
    print(f"✓ PBSServer table name: {PBSServer.__tablename__}")
    print(f"✓ Datastore table name: {Datastore.__tablename__}")
    
    # Test that models inherit from Base
    assert issubclass(PBSServer, Base), "PBSServer should inherit from Base"
    assert issubclass(Datastore, Base), "Datastore should inherit from Base"
    print("✓ Models correctly inherit from Base")
    
    # Test model methods
    pbs_server = PBSServer(
        name="test-pbs",
        hostname="pbs.example.com",
        api_token_id="test-token",
        api_token_secret="test-secret",
        datacenter="dc1"
    )
    
    print(f"✓ PBSServer connection_url: {pbs_server.connection_url}")
    print(f"✓ PBSServer is_healthy: {pbs_server.is_healthy}")
    
    print("\n🎉 All model validations passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Validation error: {e}")
    sys.exit(1)