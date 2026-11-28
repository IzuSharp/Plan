package org.korda.compare;

// Fixed independent oracle copied from the authoritative queries-v3.json, not database output.
final class Contract {
    static final String MANIFEST_SHA256 = "76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2";
    static final String[] NAMES = {"numeric", "text", "money", "json", "wide", "optional-filter", "range", "left-join", "inner-join", "null-notes", "literal-note", "customer-totals", "product-totals", "empty-sum", "cursor", "offset", "exists", "in-subquery", "cte", "window", "union-all", "union", "intersect", "except", "running-total", "three-join", "anti-association", "nullable-order", "raw-sql", "related", "tx-commit", "tx-rollback", "partial-update", "stale-conflict", "early-stop"};
    static final long[] ROWS = {32L, 32L, 32L, 32L, 32L, 32L, 32L, 32L, 32L, 32L, 32L, 9L, 32L, 1L, 32L, 32L, 1L, 32L, 32L, 32L, 32L, 24L, 8L, 8L, 32L, 32L, 32L, 32L, 32L, 53L, 3L, 3L, 3L, 2L, 3L};
    static final long[] DIGESTS = {0x68dd9f773b4eaf45L, 0xad4cf192ab829540L, 0x090e9bbb08f81c71L, 0x5d85e9fa1058a30dL, 0xc164e0de5cac73caL, 0x93ba583f1d550f3eL, 0x1e687d7ee1b01f45L, 0x8098d14e347e12ffL, 0xb514f9c828776c83L, 0x047ecbc755943285L, 0x960414b0f379ef8eL, 0x32ef708e4ab6105aL, 0xd8f8be91929cef24L, 0xaf63bd4c8601b7dfL, 0x22bcfc48e69b5245L, 0xbc492b2e59009ac5L, 0x89cd31291d2aefa4L, 0x7c5f7ec6c1ff260dL, 0xe0a534056f1e1045L, 0x6913cf7bd98734c3L, 0x373ba57117d2a6a5L, 0xd57dad5c7153e63dL, 0x1d2181af31a9863dL, 0xc4485a69ea81a02dL, 0xc4bf4fa4e24f2f39L, 0xd8acb960a36af980L, 0x014dabe6105edf0cL, 0x14e14329da4216a5L, 0xad4cf192ab829540L, 0x2785315d2691783fL, 0x2990469b2476bc94L, 0x2990469b2476bc94L, 0x7403e160cdb7c5f9L, 0x9da1fc7a0bdd78e6L, 0x9734757769760219L};
    static int index(String name) {
        for (int i=0;i<NAMES.length;i++) if (NAMES[i].equals(name)) return i;
        throw new IllegalArgumentException("Unknown case: "+name);
    }
}
