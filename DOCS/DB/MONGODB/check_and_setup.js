// Check MongoDB setup and apply schema + migrations
// Run this with: mongosh sentinel_health < check_and_setup.js

use sentinel_health;

// Check if collections exist
const collections = db.getCollectionNames();
print("Current collections:", collections);

if (!collections.includes("raw_posts")) {
    print("\n❌ ERROR: raw_posts collection does not exist!");
    print("You need to run the main schema first:");
    print("  mongosh sentinel_health < DOCS/DB/MONGODB/schema.js");
    print("\nThen run the migration:");
    print("  mongosh sentinel_health < DOCS/DB/MONGODB/migrations/001_add_replies_field.js");
} else {
    print("\n✓ raw_posts collection exists");
    
    // Check schema version
    const version = db.schema_version.findOne();
    if (version) {
        print("✓ Current schema version:", version.version);
    }
    
    // Check if migration has been applied
    const samplePost = db.raw_posts.findOne();
    if (samplePost) {
        if (samplePost.hasOwnProperty('replies')) {
            print("✓ Migration 001 already applied (replies field exists)");
        } else {
            print("⚠ Migration 001 NOT applied yet (replies field missing)");
            print("Run: mongosh sentinel_health < DOCS/DB/MONGODB/migrations/001_add_replies_field.js");
        }
    } else {
        print("⚠ No posts in raw_posts collection yet");
    }
}

print("\n========================================");
