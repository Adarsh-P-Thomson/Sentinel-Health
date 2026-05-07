// Migration 001: Remove strict validator from raw_posts
// Date: 2026-05-07
// Description: MongoDB is schemaless - no need for strict validation

use Sentinel_health;

// Remove the validator entirely - let MongoDB be flexible
db.runCommand({
  collMod: "raw_posts",
  validator: {}
});

print("✓ Migration 001 complete: Removed strict validator from raw_posts");
print("  MongoDB will now accept any fields including replies");
