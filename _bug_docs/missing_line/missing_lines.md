## 1 这两个是修复方面的问题 理应不该出现

我也不是很清楚真正会导致缺失的情况 请参见压力测试/regressioon_complex里的if...break 哪里却了一句

### 源码

``` c++
// Такт генерации бомб по области покрывающей текущий экран
screenCoverageAirStrikeTact()
{
  int airStrikeCenterX = FromScreenX(ScreenX()/2);
  int airStrikeCenterY = FromScreenY(ScreenY()/2);
  int airStrikeLeft   = airStrikeCenterX - SCREEN_COVERAGE_AIR_STRIKE_AREA_X / 2;
  int airStrikeTop    = airStrikeCenterY - SCREEN_COVERAGE_AIR_STRIKE_AREA_Y / 2;

  for(int i = 0; i < SCREEN_COVERAGE_AIR_STRIKE_BOMBS_PER_TACT; i++)
  {
    int x, y;
    // Найти случайное положение для бомбы
    do
    {
      x = airStrikeLeft + Random(SCREEN_COVERAGE_AIR_STRIKE_AREA_X);
      y = airStrikeTop + Random(SCREEN_COVERAGE_AIR_STRIKE_AREA_Y);
    } 
    while( CanPlace(AIR_STRIKE_BOMB_NVID, x, y + AIR_STRIKE_BOMB_Z, AIR_STRIKE_BOMB_Z) );
    CreateSprite(AIR_STRIKE_BOMB_NVID, x, y + AIR_STRIKE_BOMB_Z, AIR_STRIKE_BOMB_Z);
  }
}
```

### 反编译

``` c++
screenCoverageAirStrikeTact()
{
    int screenCoverageAirStrikeTact_local0;
    int screenCoverageAirStrikeTact_local1;
    int screenCoverageAirStrikeTact_local2;
    int screenCoverageAirStrikeTact_local3;
    int screenCoverageAirStrikeTact_local4;
    int screenCoverageAirStrikeTact_local5;
    int screenCoverageAirStrikeTact_local6;

    screenCoverageAirStrikeTact_local0 = FromScreenX((ScreenX() / 2));
    // --- Line 18 ---
    // --- Line 19 ---
    screenCoverageAirStrikeTact_local1 = FromScreenY((ScreenY() / 2));
    // --- Line 19 ---
    // --- Line 20 ---
    screenCoverageAirStrikeTact_local2 = (screenCoverageAirStrikeTact_local0 - 960);
    // --- Line 20 ---
    // --- Line 21 ---
    screenCoverageAirStrikeTact_local3 = (screenCoverageAirStrikeTact_local1 - 720);
    // --- Line 21 ---
    // --- Line 22 ---
    screenCoverageAirStrikeTact_local4 = 0;
    // --- Line 23 ---
    // --- Line 24 ---
    while ((screenCoverageAirStrikeTact_local4 < 20)) {
        // --- Line 26 ---
        while (1) {
            screenCoverageAirStrikeTact_local5 = (screenCoverageAirStrikeTact_local2 + Random(1920));
            // --- Line 30 ---
            screenCoverageAirStrikeTact_local6 = (screenCoverageAirStrikeTact_local3 + Random(1440));
            // --- Line 31 ---
            // --- Line 33 ---
            if ((!CanPlace(2138, screenCoverageAirStrikeTact_local5, (screenCoverageAirStrikeTact_local6 + 500), 500))) {
                CreateSprite(2138, screenCoverageAirStrikeTact_local5, (screenCoverageAirStrikeTact_local6 + 500), 500);
                // --- Line 34 --- 上一版本该语句丢失直接break
                break;
            }
        }
        CreateSprite(2138, screenCoverageAirStrikeTact_local5, (screenCoverageAirStrikeTact_local6 + 500), 500);
        // --- Line 34 ---
        (screenCoverageAirStrikeTact_local4++);
        // --- Line 24 ---
    }
    // return; mark end of function
}
```

## 2

### 源码

``` c++
// Создать иконку для миссии
createMissionIcon(int index, int globalMap)
{
  if(index == UNDEFINED_INDEX)
    return ;

  int category = categoryMission;
  int missionDifficulty = getEquipmentByCategory(EQUIPMENT_DIFFICULTY, category, index);
  int difficultyId = getDifficultyId(missionDifficulty);

  int frame = MenuFind(MAIN_CONTENT_FRAME_NVID);
  if(!frame)
    return;

  int frameScaleX = Action(frame, ACT_GET_SCALE, 0);
  int frameScaleY = Action(frame, ACT_GET_SCALE, 1);
  int frameSizeX = GetVidData(MAIN_CONTENT_FRAME_NVID, VID_SIZE_X);
  int frameSizeY = GetVidData(MAIN_CONTENT_FRAME_NVID, VID_SIZE_Y);
  frameSizeX = (frameSizeX * frameScaleX) / 1000;
  frameSizeY = (frameSizeY * frameScaleY) / 1000;
  
  string missionName = getEquipmentByCategory(EQUIPMENT_NAME, category, index);
  int iconNVid = getEquipmentByCategory(EQUIPMENT_MENU_VID, category, index, 0);
  int iconNDir = getEquipmentByCategory(EQUIPMENT_MENU_VID, category, index, 1);
  int difficultyNVid = getDifficultyNVid(difficultyId);

  // Проверка что миссии уже нет на карте чтобы не создавать дважды
  if(getSpriteByTag(missionName, difficultyNVid))
    return;

  bool onMap = getEquipmentByCategory(EQUIPMENT_ON_GLOBAL_MAP, category, index, globalMap);
  // Высчитать масштабирование объектов
  int targetScale = MenuGetProportionalInterfaceScale();
  int x;
  int y;
  int z = MISSION_ICON_Z;
  if(onMap)
  {
    x = getEquipmentByCategory(EQUIPMENT_MAP_X, category, index, globalMap);
    y = getEquipmentByCategory(EQUIPMENT_MAP_Y, category, index, globalMap);
  }
  else
  {
    int searchScale = (targetScale * GetVidData(difficultyNVid, VID_SCALE_X)) / 1000;
    int frameCenterX = ToScreenX(GetX(frame));
    int frameCenterY = ToScreenY(GetY(frame), GetZ(frame)) + (CENTER_CORRECTION_Y * searchScale) / 2000;
    int limitX = frameSizeX - GetVidData(difficultyNVid, VID_SIZE_X) * searchScale / 1000 + LIMIT_CORRECTION_X * searchScale / 2000;
    int limitY = frameSizeY - GetVidData(iconNVid,       VID_SIZE_Y) * searchScale / 1000 + LIMIT_CORRECTION_Y * searchScale / 2000; 

    // Найти не занятую область
    int maxAttempt = 200;
    int attempt = 0;
    bool goodPosition = false;
    do
    {
      attempt++;
      x = frameCenterX - limitX/2 + Random(limitX);
      y = frameCenterY - limitY/2 + Random(limitY);
      goodPosition = checkMissionPosition(x, y, searchScale, difficultyNVid, globalMap);
    }
    while(!goodPosition && (attempt < maxAttempt));

    // Выбрать текущую миссию для проставления полей
    getEquipmentByCategory(EQUIPMENT_ON_GLOBAL_MAP, category, index, globalMap);
    // Сгенерировать идёт ли дождь
    setEquipmentField(EQUIPMENT_CURRENT_RAINING,  generateRaining());
    // Сгенерировать гамму времени суток
    setEquipmentField(EQUIPMENT_CURRENT_GAMMA,    generateTimeOfDayGamma(index));
    // Записать найденное положение
    setEquipmentField(EQUIPMENT_MAP_X, globalMap,          x);
    setEquipmentField(EQUIPMENT_MAP_Y, globalMap,          y);
    // Проставить флаг что миссия показывается на глобальной карте
    setEquipmentField(EQUIPMENT_ON_GLOBAL_MAP, globalMap,  true);
  }


  // Указатель сложности
  z += MISSION_DIFFICULTY_DELTA_Z;
  int sprite = MenuCreate(difficultyNVid, 0, x, y, z, frame);
  setProportionalScale(sprite);
  Action(sprite, ACT_SET_NAME, &missionName);

  // Иконка типа миссии
  z -= MISSION_DIFFICULTY_DELTA_Z;
  y -= (MISSION_DIFFICULTY_DELTA_Y * targetScale) / 1000;
  sprite = MenuCreate(iconNVid, iconNDir, x, y, z, frame);
  setProportionalScale(sprite);
  Action(sprite, ACT_SET_NAME, &missionName);
  
  // Бордюр для иконок миссий
  int iconBorderNDir = getDifficultyBorderDir(difficultyId);
  sprite = MenuCreate(MISSION_ICON_BORDER_NVID, iconBorderNDir, x, y, z+MISSION_ICON_BORDER_DELTA_Z, frame);
  setProportionalScale(sprite);
  Action(sprite, ACT_SET_NAME, &missionName); 

  // Текст на иконке миссии
  sprite = MenuCreate(MISSION_ICON_TEXT_FONT_NVID, 0, x, y, z+MISSION_ICON_DELTA_Z, frame);
  setProportionalScale(sprite);
  Action(sprite, ACT_SET_BEHAVE, BEH_CENTER_X | BEH_CENTER_Y);
  Action(sprite, ACT_SET_NAME, &missionName);
}

```

### 反编译

``` c++
createMissionIcon(int createMissionIcon_arg0, int createMissionIcon_arg1)
{
    int createMissionIcon_local0;
    int createMissionIcon_local1;
    int createMissionIcon_local2;
    int createMissionIcon_local3;
    int createMissionIcon_local4;
    int createMissionIcon_local5;
    int createMissionIcon_local6;
    int createMissionIcon_local7;
    string createMissionIcon_local8;
    int createMissionIcon_local9;
    int createMissionIcon_local10;
    int createMissionIcon_local11;
    int createMissionIcon_local12;
    int createMissionIcon_local13;
    int createMissionIcon_local14;
    int createMissionIcon_local15;
    int createMissionIcon_local16;
    int createMissionIcon_local17;
    int createMissionIcon_local18;
    int createMissionIcon_local19;
    int createMissionIcon_local20;
    int createMissionIcon_local21;
    int createMissionIcon_local22;
    int createMissionIcon_local23;
    int createMissionIcon_local24;
    int createMissionIcon_local25;
    int createMissionIcon_local26;

    if ((createMissionIcon_arg0 == -1)) {
        return;
        // --- Line 627 ---
    }
    createMissionIcon_local0 = 15;
    // --- Line 628 ---
    // --- Line 629 ---
    createMissionIcon_local1 = getEquipmentByCategory(70, createMissionIcon_local0, createMissionIcon_arg0, -999999);
    // --- Line 629 ---
    // --- Line 630 ---
    createMissionIcon_local2 = getDifficultyId(createMissionIcon_local1);
    // --- Line 630 ---
    // --- Line 631 ---
    createMissionIcon_local3 = MenuFind(566);
    // --- Line 632 ---
    // --- Line 633 ---
    if ((!createMissionIcon_local3)) {
        return;
        // --- Line 635 ---
    }
    createMissionIcon_local4 = Action(createMissionIcon_local3, 128, 0);
    // --- Line 636 ---
    // --- Line 637 ---
    createMissionIcon_local5 = Action(createMissionIcon_local3, 128, 1);
    // --- Line 637 ---
    // --- Line 638 ---
    createMissionIcon_local6 = GetVidData(566, 239);
    // --- Line 638 ---
    // --- Line 639 ---
    createMissionIcon_local7 = GetVidData(566, 240);
    // --- Line 639 ---
    // --- Line 640 ---
    createMissionIcon_local6 = ((createMissionIcon_local6 * createMissionIcon_local4) / 1000);
    // --- Line 641 ---
    createMissionIcon_local7 = ((createMissionIcon_local7 * createMissionIcon_local5) / 1000);
    // --- Line 642 ---
    createMissionIcon_local8 = getEquipmentByCategory(44, createMissionIcon_local0, createMissionIcon_arg0, -999999);
    // --- Line 643 ---
    // --- Line 644 ---
    createMissionIcon_local9 = getEquipmentByCategory(26, createMissionIcon_local0, createMissionIcon_arg0, 0);
    // --- Line 644 ---
    // --- Line 645 ---
    createMissionIcon_local10 = getEquipmentByCategory(26, createMissionIcon_local0, createMissionIcon_arg0, 1);
    // --- Line 645 ---
    // --- Line 646 ---
    createMissionIcon_local11 = getDifficultyNVid(createMissionIcon_local2);
    // --- Line 646 ---
    // --- Line 647 ---
    if (getSpriteByTag(createMissionIcon_local8, createMissionIcon_local11)) {
        return;
        // --- Line 651 ---
    }
    createMissionIcon_local12 = getEquipmentByCategory(82, createMissionIcon_local0, createMissionIcon_arg0, createMissionIcon_arg1);
    // --- Line 652 ---
    // --- Line 653 ---
    createMissionIcon_local13 = MenuGetProportionalInterfaceScale();
    // --- Line 654 ---
    // --- Line 655 ---
    // --- Line 656 ---
    // --- Line 657 ---
    createMissionIcon_local16 = 101;
    // --- Line 657 ---
    // --- Line 658 ---
    if (createMissionIcon_local12) {
        createMissionIcon_local14 = getEquipmentByCategory(83, createMissionIcon_local0, createMissionIcon_arg0, createMissionIcon_arg1);
        // --- Line 661 ---
        createMissionIcon_local15 = getEquipmentByCategory(84, createMissionIcon_local0, createMissionIcon_arg0, createMissionIcon_arg1);
        // --- Line 662 ---
    } else {
        createMissionIcon_local17 = ((createMissionIcon_local13 * GetVidData(createMissionIcon_local11, 242)) / 1000);
        // --- Line 665 ---
        // --- Line 666 ---
        createMissionIcon_local18 = ToScreenX(GetX(createMissionIcon_local3));
        // --- Line 666 ---
        // --- Line 667 ---
        createMissionIcon_local19 = (ToScreenY(GetY(createMissionIcon_local3), GetZ(createMissionIcon_local3)) + ((117 * createMissionIcon_local17) / 2000));
        // --- Line 667 ---
        // --- Line 668 ---
        createMissionIcon_local20 = ((createMissionIcon_local6 - ((GetVidData(createMissionIcon_local11, 239) * createMissionIcon_local17) / 1000)) + ((-30 * createMissionIcon_local17) / 2000));
        // --- Line 668 ---
        // --- Line 669 ---
        createMissionIcon_local21 = ((createMissionIcon_local7 - ((GetVidData(createMissionIcon_local9, 240) * createMissionIcon_local17) / 1000)) + ((-300 * createMissionIcon_local17) / 2000));
        // --- Line 669 ---
        // --- Line 670 ---
        createMissionIcon_local22 = 200;
        // --- Line 672 ---
        // --- Line 673 ---
        createMissionIcon_local23 = 0;
        // --- Line 673 ---
        // --- Line 674 ---
        createMissionIcon_local24 = 0;
        // --- Line 674 ---
        // --- Line 675 ---
        while (1) {
            (createMissionIcon_local23++);
            // --- Line 678 ---
            createMissionIcon_local14 = ((createMissionIcon_local18 - (createMissionIcon_local20 / 2)) + Random(createMissionIcon_local20));
            // --- Line 679 ---
            createMissionIcon_local15 = ((createMissionIcon_local19 - (createMissionIcon_local21 / 2)) + Random(createMissionIcon_local21));
            // --- Line 680 ---
            createMissionIcon_local24 = checkMissionPosition(createMissionIcon_local14, createMissionIcon_local15, createMissionIcon_local17, createMissionIcon_local11, createMissionIcon_arg1);
            // --- Line 681 ---
            // --- Line 683 ---
            if ((!((!createMissionIcon_local24) && (createMissionIcon_local23 < createMissionIcon_local22)))) {
                //上一版本没有这段直接break
                getEquipmentByCategory(82, createMissionIcon_local0, createMissionIcon_arg0, createMissionIcon_arg1);
                // --- Line 686 ---
                setEquipmentField(92, generateRaining(), -999999, "");
                // --- Line 688 ---
                setEquipmentField(93, generateTimeOfDayGamma(createMissionIcon_arg0), -999999, "");
                // --- Line 690 ---
                setEquipmentField(83, createMissionIcon_arg1, createMissionIcon_local14, "");
                // --- Line 692 ---
                setEquipmentField(84, createMissionIcon_arg1, createMissionIcon_local15, "");
                // --- Line 693 ---
                setEquipmentField(82, createMissionIcon_arg1, 1, "");
                // --- Line 695 ---
                break;
            }
        }
        getEquipmentByCategory(82, createMissionIcon_local0, createMissionIcon_arg0, createMissionIcon_arg1);
        // --- Line 686 ---
        setEquipmentField(92, generateRaining(), -999999, "");
        // --- Line 688 ---
        setEquipmentField(93, generateTimeOfDayGamma(createMissionIcon_arg0), -999999, "");
        // --- Line 690 ---
        setEquipmentField(83, createMissionIcon_arg1, createMissionIcon_local14, "");
        // --- Line 692 ---
        setEquipmentField(84, createMissionIcon_arg1, createMissionIcon_local15, "");
        // --- Line 693 ---
        setEquipmentField(82, createMissionIcon_arg1, 1, "");
        // --- Line 695 ---
    }
    createMissionIcon_local16 += -2;
    // --- Line 700 ---
    createMissionIcon_local25 = MenuCreate(createMissionIcon_local11, 0, createMissionIcon_local14, createMissionIcon_local15, createMissionIcon_local16, createMissionIcon_local3);
    // --- Line 700 ---
    // --- Line 701 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 702 ---
    Action(createMissionIcon_local25, 141, (&createMissionIcon_local8));
    // --- Line 703 ---
    createMissionIcon_local16 -= -2;
    // --- Line 706 ---
    createMissionIcon_local15 -= ((42 * createMissionIcon_local13) / 1000);
    // --- Line 707 ---
    createMissionIcon_local25 = MenuCreate(createMissionIcon_local9, createMissionIcon_local10, createMissionIcon_local14, createMissionIcon_local15, createMissionIcon_local16, createMissionIcon_local3);
    // --- Line 708 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 709 ---
    Action(createMissionIcon_local25, 141, (&createMissionIcon_local8));
    // --- Line 710 ---
    createMissionIcon_local26 = getDifficultyBorderDir(createMissionIcon_local2);
    // --- Line 712 ---
    // --- Line 713 ---
    createMissionIcon_local25 = MenuCreate(2498, createMissionIcon_local26, createMissionIcon_local14, createMissionIcon_local15, (createMissionIcon_local16 + -1), createMissionIcon_local3);
    // --- Line 714 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 715 ---
    Action(createMissionIcon_local25, 141, (&createMissionIcon_local8));
    // --- Line 716 ---
    createMissionIcon_local25 = MenuCreate(5, 0, createMissionIcon_local14, createMissionIcon_local15, (createMissionIcon_local16 + 1), createMissionIcon_local3);
    // --- Line 719 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 720 ---
    Action(createMissionIcon_local25, 95, 9);
    // --- Line 721 ---
    Action(createMissionIcon_local25, 141, (&createMissionIcon_local8));
    // --- Line 722 ---
    // return; mark end of function
}
```
