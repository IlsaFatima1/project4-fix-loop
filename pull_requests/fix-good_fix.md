---
title: PR: fix calculate_total (fix/good_fix)
state: open
---

Status: OPEN
Branch: fix/good_fix
Reviewer verdict: PASS
Opened at: 2026-08-31T21:53:38.733586

Diff:
diff --git a/src/calculator.py b/src/calculator.py
index e202cb2..f2d64eb 100644
--- a/src/calculator.py
+++ b/src/calculator.py
@@ -9,4 +9,4 @@ THE BUG:
 
 def calculate_total(price, quantity):
     # BUG: addition instead of multiplication
-    return price + quantity
+    return price * quantity
