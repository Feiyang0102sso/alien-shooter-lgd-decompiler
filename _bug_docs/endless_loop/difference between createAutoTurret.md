### 旧版

``` c++
createAutoTurret(int createAutoTurret_arg0)
{
    int createAutoTurret_local0;
    int createAutoTurret_local1;
    int createAutoTurret_local2;
    int createAutoTurret_local3;
    int createAutoTurret_local4;
    int createAutoTurret_local5;
    int createAutoTurret_local6;
    int createAutoTurret_local7;
    int createAutoTurret_local8;
    int createAutoTurret_local9;
    int createAutoTurret_local10;
    int createAutoTurret_local11;
    int createAutoTurret_local12;

    createAutoTurret_local0 = Flagman(0);
    // --- Line 167 ---
    // --- Line 168 ---
    if ((!createAutoTurret_local0)) {
        return 0;
        // --- Line 170 ---
    }
    createAutoTurret_local1 = GetDirection(createAutoTurret_local0);
    // --- Line 172 ---
    // --- Line 173 ---
    createAutoTurret_local2 = GetX(createAutoTurret_local0);
    // --- Line 173 ---
    // --- Line 174 ---
    createAutoTurret_local3 = GetY(createAutoTurret_local0);
    // --- Line 174 ---
    // --- Line 175 ---
    createAutoTurret_local4 = GetZ(createAutoTurret_local0);
    // --- Line 175 ---
    // --- Line 176 ---
    createAutoTurret_local2 += ((90 * Sin(createAutoTurret_local1)) / 1024);
    // --- Line 177 ---
    createAutoTurret_local3 -= ((90 * Cos(createAutoTurret_local1)) / 1024);
    // --- Line 178 ---
    createAutoTurret_local5 = CreateSprite(createAutoTurret_arg0, -10000, -10000, createAutoTurret_local4, createAutoTurret_local1);
    // --- Line 178 ---
    // --- Line 179 ---
    if ((!createAutoTurret_local5)) {
        return 0;
        // --- Line 181 ---
    }
    if (isSafePlaceForAutoTurretCreation(createAutoTurret_arg0, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local0)) {
        Action(createAutoTurret_local5, 63, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local4);
        // --- Line 188 ---
        return 1;
        // --- Line 189 ---
    }
    createAutoTurret_local6 = createAutoTurret_local2;
    // --- Line 192 ---
    // --- Line 193 ---
    createAutoTurret_local7 = createAutoTurret_local3;
    // --- Line 193 ---
    // --- Line 194 ---
    logDebug(((("AutoTurretCreation: Search for safe p..." + itoa(createAutoTurret_local2)) + " y = ") + itoa(createAutoTurret_local3)));
    // --- Line 195 ---
    createAutoTurret_local8 = 0;
    // --- Line 195 ---
    // --- Line 196 ---
    createAutoTurret_local9 = 20;
    // --- Line 196 ---
    // --- Line 197 ---
    createAutoTurret_local10 = 0;
    // --- Line 198 ---
    // --- Line 199 ---
    (++createAutoTurret_local8);
    // --- Line 203 ---
    while ((createAutoTurret_local8 == createAutoTurret_local9)) {
        createAutoTurret_local11 = (10 + Random(80));
        // --- Line 207 ---
        // --- Line 208 ---
        createAutoTurret_local12 = Random(255);
        // --- Line 208 ---
        // --- Line 209 ---
        createAutoTurret_local2 = (createAutoTurret_local6 + ((createAutoTurret_local11 * Sin(createAutoTurret_local12)) / 1024));
        // --- Line 212 ---
        createAutoTurret_local3 = (createAutoTurret_local7 - ((createAutoTurret_local11 * Cos(createAutoTurret_local12)) / 1024));
        // --- Line 213 ---
        createAutoTurret_local10 = isSafePlaceForAutoTurretCreation(createAutoTurret_arg0, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local0);
        // --- Line 216 ---
        if (!createAutoTurret_local10) {

        }
        // --- Line 219 ---
        if (createAutoTurret_local10) {
            Action(createAutoTurret_local5, 63, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local4);
            // --- Line 227 ---
            return 1;
            // --- Line 228 ---
        }
        if (createAutoTurret_local5) {
            Destroy(createAutoTurret_local5);
            // --- Line 259 ---
        }
        return 0;
        // --- Line 261 ---
    }
    // --- Line 219 ---
    if (createAutoTurret_local10) {
        Action(createAutoTurret_local5, 63, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local4);
        // --- Line 227 ---
        return 1;
        // --- Line 228 ---
    }
    if (createAutoTurret_local5) {
        Destroy(createAutoTurret_local5);
        // --- Line 259 ---
    }
    return 0;
    // --- Line 261 ---
}

```

### 新版

``` c++
createAutoTurret(int createAutoTurret_arg0)
{
    int createAutoTurret_local0;
    int createAutoTurret_local1;
    int createAutoTurret_local2;
    int createAutoTurret_local3;
    int createAutoTurret_local4;
    int createAutoTurret_local5;
    int createAutoTurret_local6;
    int createAutoTurret_local7;
    int createAutoTurret_local8;
    int createAutoTurret_local9;
    int createAutoTurret_local10;
    int createAutoTurret_local11;
    int createAutoTurret_local12;

    createAutoTurret_local0 = Flagman(0);
    // --- Line 167 ---
    // --- Line 168 ---
    if ((!createAutoTurret_local0)) {
        return 0;
        // --- Line 170 ---
    }
    createAutoTurret_local1 = GetDirection(createAutoTurret_local0);
    // --- Line 172 ---
    // --- Line 173 ---
    createAutoTurret_local2 = GetX(createAutoTurret_local0);
    // --- Line 173 ---
    // --- Line 174 ---
    createAutoTurret_local3 = GetY(createAutoTurret_local0);
    // --- Line 174 ---
    // --- Line 175 ---
    createAutoTurret_local4 = GetZ(createAutoTurret_local0);
    // --- Line 175 ---
    // --- Line 176 ---
    createAutoTurret_local2 += ((90 * Sin(createAutoTurret_local1)) / 1024);
    // --- Line 177 ---
    createAutoTurret_local3 -= ((90 * Cos(createAutoTurret_local1)) / 1024);
    // --- Line 178 ---
    createAutoTurret_local5 = CreateSprite(createAutoTurret_arg0, -10000, -10000, createAutoTurret_local4, createAutoTurret_local1);
    // --- Line 178 ---
    // --- Line 179 ---
    if ((!createAutoTurret_local5)) {
        return 0;
        // --- Line 181 ---
    }
    if (isSafePlaceForAutoTurretCreation(createAutoTurret_arg0, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local0)) {
        Action(createAutoTurret_local5, 63, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local4);
        // --- Line 188 ---
        return 1;
        // --- Line 189 ---
    }
    createAutoTurret_local6 = createAutoTurret_local2;
    // --- Line 192 ---
    // --- Line 193 ---
    createAutoTurret_local7 = createAutoTurret_local3;
    // --- Line 193 ---
    // --- Line 194 ---
    logDebug(((("AutoTurretCreation: Search for safe p..." + itoa(createAutoTurret_local2)) + " y = ") + itoa(createAutoTurret_local3)));
    // --- Line 195 ---
    createAutoTurret_local8 = 0;
    // --- Line 195 ---
    // --- Line 196 ---
    createAutoTurret_local9 = 20;
    // --- Line 196 ---
    // --- Line 197 ---
    createAutoTurret_local10 = 0;
    // --- Line 198 ---
    // --- Line 199 ---
    while (1) {
        (++createAutoTurret_local8);
        // --- Line 203 ---
        if ((createAutoTurret_local8 == createAutoTurret_local9)) {
            break;
        }
        createAutoTurret_local11 = (10 + Random(80));
        // --- Line 207 ---
        // --- Line 208 ---
        createAutoTurret_local12 = Random(255);
        // --- Line 208 ---
        // --- Line 209 ---
        createAutoTurret_local2 = (createAutoTurret_local6 + ((createAutoTurret_local11 * Sin(createAutoTurret_local12)) / 1024));
        // --- Line 212 ---
        createAutoTurret_local3 = (createAutoTurret_local7 - ((createAutoTurret_local11 * Cos(createAutoTurret_local12)) / 1024));
        // --- Line 213 ---
        createAutoTurret_local10 = isSafePlaceForAutoTurretCreation(createAutoTurret_arg0, createAutoTurret_local2, createAutoTurret_local3, createAutoTurret_local0);
        // --- Line 216 ---
        if (!createAutoTurret_local10) {
            break;
        }

```

