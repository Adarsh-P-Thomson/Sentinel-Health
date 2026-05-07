// Check if raw_posts has a validator

use Sentinel_health;

const collInfo = db.getCollectionInfos({ name: "raw_posts" });

if (collInfo.length > 0) {
    print("✓ raw_posts collection exists");
    
    if (collInfo[0].options && collInfo[0].options.validator) {
        print("⚠ Collection HAS a validator");
        print(JSON.stringify(collInfo[0].options.validator, null, 2));
    } else {
        print("✓ Collection has NO validator (schemaless - accepts any fields)");
        print("  No migration needed!");
    }
} else {
    print("❌ raw_posts collection does NOT exist");
}
