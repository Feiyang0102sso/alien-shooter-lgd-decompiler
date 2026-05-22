我要测试我的反编译器是否出现 while(1)但没有 break
或者 while (xxxxx){空} 等死循环情况 这属于哪种测试
目前没想到还有啥其他情况会造成死循环 至少我只发现了两种 它们都是由 do-while产生的 (大概)

我记得上次修复是修复了do while的bug 但很显然修的不是很全面

## 修复内容

主要是(循环体有 2 个及以上基本块的情况 方面的

### 源码

``` c++
SurviveGameTact()
{
  static int prev_time=0, prev_shift=-1;
  static int arrowed_unit=0;
  int        shift,i,x,y,delta_speed,dir,unit;
  if( (GetTime()-prev_time)>100 )
  {
    prev_time = GetTime();
    shift = (startSurviveShift + (GetTime()-StartGameTime)/30000)*24;
    if( shift > 39*24 )
      shift = 39*24;
    if( shift!=prev_shift )
    {
      prev_shift = shift;
      for( i = 0; i < sizeof(MonstersVid)/4; i++ )
      {
        delta_speed = (GetVidData(MonstersVid[i],VID_SPEED)*MonsterSpeedPercent[shift/24])/100;
        SetVidData(MonstersVid[i],VID_SPEED,GetVidData(MonstersVid[i],VID_SPEED) + delta_speed);
      }
    }
    for( i = 0; i < 24; i++ )
      if( MonsterBirthP[shift+i] )
      {
        if( !Random( 600/MonsterBirthP[shift+i] - 1 ) ||
            (MonsterBirthP[shift+i]==1 && ((GetTime()-StartGameTime)%30000) > 15000) )//если в этой минуте должен был родится 1 монстр и не родился за 55 секунд то рожаем
        {
          do
          {
            x=Random(3);
            if     ( x==0 ) { x=-50;                y=Random(MapSizeY()); }
            else if( x==1 ) { x=MapSizeX()+50;      y=Random(MapSizeY()); }
            else if( x==2 ) { x=Random(MapSizeX()); y=-50;                }
            else            { x=Random(MapSizeX()); y=MapSizeY()+50;      }
          } while( CanPlace(MonstersVid[i],x,y,0) );
//          Action( CreateSprite((4+i/3)*10+(i%3)*3,x,y,0), ACT_ATTACK,Flagman(0),0);
          unit = CreateSprite(MonstersVid[i],x,y,0);
          Action( unit, ACT_ATTACK,Flagman(0),0);
          if( IsBossVid( MonstersVid[i] ) )
            arrowed_unit = unit;
          if( MonsterBirthP[shift+i] == 1 )
            MonsterBirthP[shift+i] = 0;
        }
      }
    if( Flagman(0) )
    {
      if( arrowed_unit )
      {
        if( !ArrowHint )
          ArrowHint = CreateSprite(786,GetX(Flagman(0)),GetY(Flagman(0)),GetZ(Flagman(0)));
      }
      else if( ArrowHint )
      {
        Destroy(ArrowHint);
        ArrowHint = 0;
      }
    }
  }
  if( ArrowHint )
    if( arrowed_unit )
    {
      dir = DirectionTo(Flagman(0),GetX(arrowed_unit),GetY(arrowed_unit));
      Action(ArrowHint,ACT_CHANGE_DIRECTION,dir);
//        Action(ArrowHint,ACT_CHANGE_COOR,GetX(Flagman(0)),GetY(Flagman(0)),GetZ(Flagman(0))+11);
      Action(ArrowHint,ACT_CHANGE_COOR,GetX(Flagman(0))+Sin(dir)/25,GetY(Flagman(0))-Cos(dir)/25,GetZ(Flagman(0)));
    }
}

```

### 反编译

``` c++
SurviveGameTact()
{
    static int SurviveGameTact_local0 = 0;
    static int SurviveGameTact_local1 = -1;
    static int SurviveGameTact_local2 = 0;
    int SurviveGameTact_local3;
    int SurviveGameTact_local4;
    int SurviveGameTact_local5;
    int SurviveGameTact_local6;
    int SurviveGameTact_local7;
    int SurviveGameTact_local8;
    int SurviveGameTact_local9;

    // --- Line 8612 ---
    // --- Line 8613 ---
    // --- Line 8614 ---
    // --- Line 8615 ---
    // --- Line 8616 ---
    // --- Line 8617 ---
    // --- Line 8618 ---
    // --- Line 8619 ---
    // --- Line 8620 ---
    // --- Line 8621 ---
    if (((GetTime() - SurviveGameTact_local0) > 100)) {
        SurviveGameTact_local0 = GetTime();
        // --- Line 8627 ---
        SurviveGameTact_local3 = ((startSurviveShift + ((GetTime() - StartGameTime) / 30000)) * 24);
        // --- Line 8629 ---
        if ((SurviveGameTact_local3 > 936)) {
            SurviveGameTact_local3 = 936;
            // --- Line 8632 ---
        }
        if ((SurviveGameTact_local3 != SurviveGameTact_local1)) {
            SurviveGameTact_local1 = SurviveGameTact_local3;
            // --- Line 8636 ---
            for (SurviveGameTact_local4 = 0; (SurviveGameTact_local4 < 26); (SurviveGameTact_local4++)) {
                SurviveGameTact_local7 = ((GetVidData(MonstersVid[SurviveGameTact_local4], 48) * MonsterSpeedPercent[(SurviveGameTact_local3 / 24)]) / 100);
                // --- Line 8639 ---
                SetVidData(MonstersVid[SurviveGameTact_local4], 48, (GetVidData(MonstersVid[SurviveGameTact_local4], 48) + SurviveGameTact_local7));
                // --- Line 8641 ---
            }
        }
        for (SurviveGameTact_local4 = 0; (SurviveGameTact_local4 < 24); (SurviveGameTact_local4++)) {
            if (MonsterBirthP[(SurviveGameTact_local3 + SurviveGameTact_local4)]) {
            if (((!Random(((600 / MonsterBirthP[(SurviveGameTact_local3 + SurviveGameTact_local4)]) - 1))) || ((MonsterBirthP[(SurviveGameTact_local3 + SurviveGameTact_local4)] == 1) && (((GetTime() - StartGameTime) % 30000) > 15000)))) {
            while (1) {
            SurviveGameTact_local5 = Random(3);
            // --- Line 8649 ---
            if ((SurviveGameTact_local5 == 0)) {
            SurviveGameTact_local5 = -50;
            // --- Line 8652 ---
            SurviveGameTact_local6 = Random(MapSizeY());
            // --- Line 8654 ---
            } else if ((SurviveGameTact_local5 == 1)) {
            SurviveGameTact_local5 = (MapSizeX() + 50);
            // --- Line 8657 ---
            SurviveGameTact_local6 = Random(MapSizeY());
            // --- Line 8659 ---
            } else if ((SurviveGameTact_local5 == 2)) {
            SurviveGameTact_local5 = Random(MapSizeX());
            // --- Line 8662 ---
            SurviveGameTact_local6 = -50;
            // --- Line 8664 ---
            } else {
            SurviveGameTact_local5 = Random(MapSizeX());
            // --- Line 8667 ---
            SurviveGameTact_local6 = (MapSizeY() + 50);
            // --- Line 8669 ---
            }
            if ((!CanPlace(MonstersVid[SurviveGameTact_local4], SurviveGameTact_local5, SurviveGameTact_local6, 0))) {
            break;
            }
            }
            SurviveGameTact_local9 = CreateSprite(MonstersVid[SurviveGameTact_local4], SurviveGameTact_local5, SurviveGameTact_local6, 0);
            // --- Line 8677 ---
            Action(SurviveGameTact_local9, 32, Flagman(0), 0);
            // --- Line 8679 ---
            if (IsBossVid(MonstersVid[SurviveGameTact_local4])) {
            SurviveGameTact_local2 = SurviveGameTact_local9;
            // --- Line 8682 ---
            }
            if ((MonsterBirthP[(SurviveGameTact_local3 + SurviveGameTact_local4)] == 1)) {
            MonsterBirthP[(SurviveGameTact_local3 + SurviveGameTact_local4)] = 0;
            // --- Line 8686 ---
            }
            }
            }
        }
        if (Flagman(0)) {
            if (SurviveGameTact_local2) {
                if ((!ArrowHint)) {
                    ArrowHint = CreateSprite(786, GetX(Flagman(0)), GetY(Flagman(0)), GetZ(Flagman(0)));
                    // --- Line 8695 ---
                }
            } else if (ArrowHint) {
                Destroy(ArrowHint);
                // --- Line 8699 ---
                ArrowHint = 0;
                // --- Line 8701 ---
            }
        }
    }
    if (ArrowHint) {
        if (SurviveGameTact_local2) {
            SurviveGameTact_local8 = DirectionTo(Flagman(0), GetX(SurviveGameTact_local2), GetY(SurviveGameTact_local2));
            // --- Line 8708 ---
            Action(ArrowHint, 60, SurviveGameTact_local8);
            // --- Line 8710 ---
            Action(ArrowHint, 63, (GetX(Flagman(0)) + (Sin(SurviveGameTact_local8) / 25)), (GetY(Flagman(0)) - (Cos(SurviveGameTact_local8) / 25)), GetZ(Flagman(0)));
            // --- Line 8712 ---
        }
    }
    // return; mark end of function
}

```

## 并未修复内容

### 1

#### 源码

``` c++
createEnemyInPosition(int nVid, int aX, int aY, int aZ)
{
  int maxRandom = ENEMY_BIRTH_MAX_DISTANCE * 2;
  // Найти случайное положение для юнита
  int x;
  int y;
  int i = 0;
  do
  {
    ++i;
    x = aX + ENEMY_BIRTH_MAX_DISTANCE - Random(maxRandom);
    y = aY + ENEMY_BIRTH_MAX_DISTANCE - Random(maxRandom);
    //Log("XXXCCC createEnemyInPosition x = " + itoa(x) + ",  y = " + itoa(y) + ",  aZ = " +itoa(aZ));
  } 
  while (CanPlace(nVid, x, y, aZ) && (i < ENEMY_BIRTH_ATTEMPTS));

  // Не удалось найти позицию для рождения
  if (i == ENEMY_BIRTH_ATTEMPTS)
    return 0;
  //Log("XXXCCC createEnemyInPosition nVid = " + itoa(nVid));
  // Создать юнит
  int unit = CreateSprite(nVid, x, y, aZ);
  // Перекрасить юнита в гамму текущего уровня монстров
  Action(unit, ACT_SET_GAMMA, currentEnemyLevelGamma);
  return unit;
}


```

#### 反

``` c++
createEnemyInPosition(int createEnemyInPosition_arg0, int createEnemyInPosition_arg1, int createEnemyInPosition_arg2, int createEnemyInPosition_arg3)
{
    int createEnemyInPosition_local0;
    int createEnemyInPosition_local1;
    int createEnemyInPosition_local2;
    int createEnemyInPosition_local3;
    int createEnemyInPosition_local4;

    createEnemyInPosition_local0 = 100;
    // --- Line 598 ---
    // --- Line 599 ---
    // --- Line 601 ---
    // --- Line 602 ---
    createEnemyInPosition_local3 = 0;
    // --- Line 602 ---
    // --- Line 603 ---
    (++createEnemyInPosition_local3);
    // --- Line 606 ---
    createEnemyInPosition_local1 = ((createEnemyInPosition_arg1 + 50) - Random(createEnemyInPosition_local0));
    // --- Line 607 ---
    createEnemyInPosition_local2 = ((createEnemyInPosition_arg2 + 50) - Random(createEnemyInPosition_local0));
    // --- Line 608 ---
    // --- Line 611 ---
    while (CanPlace(createEnemyInPosition_arg0, createEnemyInPosition_local1, createEnemyInPosition_local2, createEnemyInPosition_arg3) && (createEnemyInPosition_local3 < 10)) {

    }
    if ((createEnemyInPosition_local3 == 10)) {
        return 0;
        // --- Line 615 ---
    }
    createEnemyInPosition_local4 = CreateSprite(createEnemyInPosition_arg0, createEnemyInPosition_local1, createEnemyInPosition_local2, createEnemyInPosition_arg3);
    // --- Line 617 ---
    // --- Line 618 ---
    Action(createEnemyInPosition_local4, ACT_SET_GAMMA, currentEnemyLevelGamma);
    // --- Line 620 ---
    return createEnemyInPosition_local4;
    // --- Line 621 ---
}

```

### 2

#### 源码

``` c++
moveEnemyToPosition(int unit, int aX, int aY, int aZ)
{
  int maxRandom = ENEMY_BIRTH_MAX_DISTANCE * 2;
  // Найти случайное положение для юнита
  int x;
  int y;
  int nVid = GetUnitVid(unit);
  int i = 0;
  do
  {
    ++i;
    x = aX + ENEMY_BIRTH_MAX_DISTANCE - Random(maxRandom);
    y = aY + ENEMY_BIRTH_MAX_DISTANCE - Random(maxRandom);
  } 
  while( CanPlace(nVid, x, y, aZ) && (i < ENEMY_BIRTH_ATTEMPTS) );
  // Не удалось найти позицию для рождения
  if (i == ENEMY_BIRTH_ATTEMPTS)
    return 0;

  Action(unit, ACT_CHANGE_COOR, x, y, aZ);
  return unit;
}
```

#### 反

``` c++
moveEnemyToPosition(int moveEnemyToPosition_arg0, int moveEnemyToPosition_arg1, int moveEnemyToPosition_arg2, int moveEnemyToPosition_arg3)
{
    int moveEnemyToPosition_local0;
    int moveEnemyToPosition_local1;
    int moveEnemyToPosition_local2;
    int moveEnemyToPosition_local3;
    int moveEnemyToPosition_local4;

    moveEnemyToPosition_local0 = 100;
    // --- Line 627 ---
    // --- Line 628 ---
    // --- Line 630 ---
    // --- Line 631 ---
    moveEnemyToPosition_local3 = GetUnitVid(moveEnemyToPosition_arg0);
    // --- Line 631 ---
    // --- Line 632 ---
    moveEnemyToPosition_local4 = 0;
    // --- Line 632 ---
    // --- Line 633 ---
    (++moveEnemyToPosition_local4);
    // --- Line 636 ---
    moveEnemyToPosition_local1 = ((moveEnemyToPosition_arg1 + 50) - Random(moveEnemyToPosition_local0));
    // --- Line 637 ---
    moveEnemyToPosition_local2 = ((moveEnemyToPosition_arg2 + 50) - Random(moveEnemyToPosition_local0));
    // --- Line 638 ---
    // --- Line 640 ---
    while (CanPlace(moveEnemyToPosition_local3, moveEnemyToPosition_local1, moveEnemyToPosition_local2, moveEnemyToPosition_arg3) && (moveEnemyToPosition_local4 < 10)) {

    }
    if ((moveEnemyToPosition_local4 == 10)) {
        return 0;
        // --- Line 643 ---
    }
    Action(moveEnemyToPosition_arg0, ACT_CHANGE_COOR, moveEnemyToPosition_local1, moveEnemyToPosition_local2, moveEnemyToPosition_arg3);
    // --- Line 645 ---
    return moveEnemyToPosition_arg0;
    // --- Line 646 ---
}

```

### 3

#### 源码

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

#### 反

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
    createMissionIcon_local4 = Action(createMissionIcon_local3, ACT_GET_SCALE, 0);
    // --- Line 636 ---
    // --- Line 637 ---
    createMissionIcon_local5 = Action(createMissionIcon_local3, ACT_GET_SCALE, 1);
    // --- Line 637 ---
    // --- Line 638 ---
    createMissionIcon_local6 = GetVidData(566, VID_SIZE_X);
    // --- Line 638 ---
    // --- Line 639 ---
    createMissionIcon_local7 = GetVidData(566, VID_SIZE_Y);
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
        createMissionIcon_local17 = ((createMissionIcon_local13 * GetVidData(createMissionIcon_local11, VID_SCALE_X)) / 1000);
        // --- Line 665 ---
        // --- Line 666 ---
        createMissionIcon_local18 = ToScreenX(GetX(createMissionIcon_local3));
        // --- Line 666 ---
        // --- Line 667 ---
        createMissionIcon_local19 = (ToScreenY(GetY(createMissionIcon_local3), GetZ(createMissionIcon_local3)) + ((117 * createMissionIcon_local17) / 2000));
        // --- Line 667 ---
        // --- Line 668 ---
        createMissionIcon_local20 = ((createMissionIcon_local6 - ((GetVidData(createMissionIcon_local11, VID_SIZE_X) * createMissionIcon_local17) / 1000)) + ((-30 * createMissionIcon_local17) / 2000));
        // --- Line 668 ---
        // --- Line 669 ---
        createMissionIcon_local21 = ((createMissionIcon_local7 - ((GetVidData(createMissionIcon_local9, VID_SIZE_Y) * createMissionIcon_local17) / 1000)) + ((-300 * createMissionIcon_local17) / 2000));
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
        (createMissionIcon_local23++);
        // --- Line 678 ---
        createMissionIcon_local14 = ((createMissionIcon_local18 - (createMissionIcon_local20 / 2)) + Random(createMissionIcon_local20));
        // --- Line 679 ---
        createMissionIcon_local15 = ((createMissionIcon_local19 - (createMissionIcon_local21 / 2)) + Random(createMissionIcon_local21));
        // --- Line 680 ---
        createMissionIcon_local24 = checkMissionPosition(createMissionIcon_local14, createMissionIcon_local15, createMissionIcon_local17, createMissionIcon_local11, createMissionIcon_arg1);
        // --- Line 681 ---
        // --- Line 683 ---
        while ((!createMissionIcon_local24) && (createMissionIcon_local23 < createMissionIcon_local22)) {

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
    Action(createMissionIcon_local25, ACT_SET_NAME, (&createMissionIcon_local8));
    // --- Line 703 ---
    createMissionIcon_local16 -= -2;
    // --- Line 706 ---
    createMissionIcon_local15 -= ((42 * createMissionIcon_local13) / 1000);
    // --- Line 707 ---
    createMissionIcon_local25 = MenuCreate(createMissionIcon_local9, createMissionIcon_local10, createMissionIcon_local14, createMissionIcon_local15, createMissionIcon_local16, createMissionIcon_local3);
    // --- Line 708 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 709 ---
    Action(createMissionIcon_local25, ACT_SET_NAME, (&createMissionIcon_local8));
    // --- Line 710 ---
    createMissionIcon_local26 = getDifficultyBorderDir(createMissionIcon_local2);
    // --- Line 712 ---
    // --- Line 713 ---
    createMissionIcon_local25 = MenuCreate(2498, createMissionIcon_local26, createMissionIcon_local14, createMissionIcon_local15, (createMissionIcon_local16 + -1), createMissionIcon_local3);
    // --- Line 714 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 715 ---
    Action(createMissionIcon_local25, ACT_SET_NAME, (&createMissionIcon_local8));
    // --- Line 716 ---
    createMissionIcon_local25 = MenuCreate(5, 0, createMissionIcon_local14, createMissionIcon_local15, (createMissionIcon_local16 + 1), createMissionIcon_local3);
    // --- Line 719 ---
    setProportionalScale(createMissionIcon_local25);
    // --- Line 720 ---
    Action(createMissionIcon_local25, ACT_SET_BEHAVE, 9);
    // --- Line 721 ---
    Action(createMissionIcon_local25, ACT_SET_NAME, (&createMissionIcon_local8));
    // --- Line 722 ---
    // return; mark end of function
}

```





### 4 接下来几个并非bug 本来就这么写的

#### 源码

``` c++
// Выставить значение параметра indicatorIndex для поля соответствующего indType
setMarketIndexedParameter(int indicatorIndex, int indType, int index, int sliderIndex)
{
  // Тэг элементов интерфейса
  string tagPostfix =  itoa(indicatorIndex);
  string resultBaseTag = "tag_slider_" + itoa(sliderIndex) + "_indicator_" ;
  // Поменять теги элементов
  while(changeLoadingElementTag(tagPostfix, resultBaseTag, ITEM_INDICATOR_MARKET_BASE_TAG))
    ;

  // Соответствия иконок индексированных индикаторов
  string tag = resultBaseTag + tagPostfix;
  int icon = iconForIndicator(indType);
  setIndicatorIcon(tag, icon);
  // Выставить значение параметра tagName для поля 
  setMarketParameterForField(tag, indType, index);
}
```

#### 反

``` c++
setMarketIndexedParameter(int setMarketIndexedParameter_arg0, int setMarketIndexedParameter_arg1, int setMarketIndexedParameter_arg2, int setMarketIndexedParameter_arg3)
{
    string setMarketIndexedParameter_local0;
    string setMarketIndexedParameter_local1;
    string setMarketIndexedParameter_local2;
    int setMarketIndexedParameter_local3;

    setMarketIndexedParameter_local0 = itoa(setMarketIndexedParameter_arg0);
    // --- Line 194 ---
    // --- Line 195 ---
    setMarketIndexedParameter_local1 = (("tag_slider_" + itoa(setMarketIndexedParameter_arg3)) + "_indicator_");
    // --- Line 195 ---
    // --- Line 196 ---
    // --- Line 199 ---
    while (changeLoadingElementTag(setMarketIndexedParameter_local0, setMarketIndexedParameter_local1, "tag_indicator_market_")) {

    }
    setMarketIndexedParameter_local2 = (setMarketIndexedParameter_local1 + setMarketIndexedParameter_local0);
    // --- Line 201 ---
    // --- Line 202 ---
    setMarketIndexedParameter_local3 = iconForIndicator(setMarketIndexedParameter_arg1);
    // --- Line 202 ---
    // --- Line 203 ---
    setIndicatorIcon(setMarketIndexedParameter_local2, setMarketIndexedParameter_local3);
    // --- Line 204 ---
    setMarketParameterForField(setMarketIndexedParameter_local2, setMarketIndexedParameter_arg1, setMarketIndexedParameter_arg2);
    // --- Line 206 ---
    // return; mark end of function
}

```

### 5

#### 源码

``` c++
// Выставить значение параметра indicatorIndex для поля соответствующего indType
setBlackMarketIndexedParameter(int indicatorIndex, int indType, int category, int index, int sliderIndex)
{
  // Тэг элементов интерфейса
  string tagPostfix =  itoa(indicatorIndex);
  string resultBaseTag = "tag_slider_" + itoa(sliderIndex) + "_indicator_" ;
  // Поменять теги элементов
  while(changeLoadingElementTag(tagPostfix, resultBaseTag, ITEM_INDICATOR_MARKET_BASE_TAG))
    ;

  // Соответствия иконок индексированных индикаторов
  string tag = resultBaseTag + tagPostfix;
  // Выставить значение параметра indicatorIndex для поля соответствующего indType
  setTemplateInfoIndexedParameter(indicatorIndex, indType, category, index, tag);
}
```

#### 反

``` c++
setBlackMarketIndexedParameter(int setBlackMarketIndexedParameter_arg0, int setBlackMarketIndexedParameter_arg1, int setBlackMarketIndexedParameter_arg2, int setBlackMarketIndexedParameter_arg3, int setBlackMarketIndexedParameter_arg4)
{
    string setBlackMarketIndexedParameter_local0;
    string setBlackMarketIndexedParameter_local1;
    string setBlackMarketIndexedParameter_local2;

    setBlackMarketIndexedParameter_local0 = itoa(setBlackMarketIndexedParameter_arg0);
    // --- Line 173 ---
    // --- Line 174 ---
    setBlackMarketIndexedParameter_local1 = (("tag_slider_" + itoa(setBlackMarketIndexedParameter_arg4)) + "_indicator_");
    // --- Line 174 ---
    // --- Line 175 ---
    // --- Line 178 ---
    while (changeLoadingElementTag(setBlackMarketIndexedParameter_local0, setBlackMarketIndexedParameter_local1, "tag_indicator_market_")) {

    }
    setBlackMarketIndexedParameter_local2 = (setBlackMarketIndexedParameter_local1 + setBlackMarketIndexedParameter_local0);
    // --- Line 180 ---
    // --- Line 181 ---
    setTemplateInfoIndexedParameter(setBlackMarketIndexedParameter_arg0, setBlackMarketIndexedParameter_arg1, setBlackMarketIndexedParameter_arg2, setBlackMarketIndexedParameter_arg3, setBlackMarketIndexedParameter_local2);
    // --- Line 183 ---
    // return; mark end of function
}

```

### 6

#### 源码

``` c++
// Выставить значение мажорного параметра перка шаблона для поля соответствующего indType
setBlackMarketMajorPerkParameter(int indicatorIndex, int category, int index, int sliderIndex)
{
  // Тэг элементов интерфейса
  string tagPostfix =  itoa(indicatorIndex);
  string resultBaseTag = "tag_slider_" + itoa(sliderIndex) + "_indicator_" ;
  // Поменять теги элементов
  while(changeLoadingElementTag(tagPostfix, resultBaseTag, ITEM_INDICATOR_MARKET_BASE_TAG))
    ;

  // Выставить значение мажорного параметра перка шаблона для поля соответствующего indType
  string tag = resultBaseTag + tagPostfix;
  setTemplateMajorPerkParameter(category, index, indicatorIndex, tag);
}

```

#### 反

``` c++
setBlackMarketMajorPerkParameter(int setBlackMarketMajorPerkParameter_arg0, int setBlackMarketMajorPerkParameter_arg1, int setBlackMarketMajorPerkParameter_arg2, int setBlackMarketMajorPerkParameter_arg3)
{
    string setBlackMarketMajorPerkParameter_local0;
    string setBlackMarketMajorPerkParameter_local1;
    string setBlackMarketMajorPerkParameter_local2;

    setBlackMarketMajorPerkParameter_local0 = itoa(setBlackMarketMajorPerkParameter_arg0);
    // --- Line 190 ---
    // --- Line 191 ---
    setBlackMarketMajorPerkParameter_local1 = (("tag_slider_" + itoa(setBlackMarketMajorPerkParameter_arg3)) + "_indicator_");
    // --- Line 191 ---
    // --- Line 192 ---
    // --- Line 195 ---
    while (changeLoadingElementTag(setBlackMarketMajorPerkParameter_local0, setBlackMarketMajorPerkParameter_local1, "tag_indicator_market_")) {

    }
    setBlackMarketMajorPerkParameter_local2 = (setBlackMarketMajorPerkParameter_local1 + setBlackMarketMajorPerkParameter_local0);
    // --- Line 197 ---
    // --- Line 198 ---
    setTemplateMajorPerkParameter(setBlackMarketMajorPerkParameter_arg1, setBlackMarketMajorPerkParameter_arg2, setBlackMarketMajorPerkParameter_arg0, setBlackMarketMajorPerkParameter_local2);
    // --- Line 199 ---
    // return; mark end of function
}

```

### 7

#### 源码

``` c++
// Фрейм параметров
slider_black_market_parameters(int image, int sliderIndex)
{
  int category = blackMarketCategory(sliderIndex);
  int index = blackMarketIndex(sliderIndex);

  // Очистить содержимое
  loadToFrameBySprite(image, FRAME_EMPTY);
  
  // Загрузить список параметров
  loadToFrameBySprite(image, FRAME_BLACK_MARKET_PARAMETERS_MENU);

  // Выставить значения параметров 
  int indicatorIndex;
  int usedIndicatorCount = 0;
  for (indicatorIndex = 0; indicatorIndex < MAX_INDICATORS; ++indicatorIndex)
  {
    int indType = UNDEFINED_VALUE;
    indType = getEquipmentByCategory(EQUIPMENT_INDICATOR, category, index, indicatorIndex); 
    if (indType != UNDEFINED_VALUE)
    {
      setBlackMarketIndexedParameter(usedIndicatorCount, indType, category, index, sliderIndex);
      ++usedIndicatorCount;
    }
    else
      ;//hideIndexedParameter(indicatorIndex);
  }

  // Выставить значение мажорного параметра перка шаблона для поля соответствующего indType
  setBlackMarketMajorPerkParameter(usedIndicatorCount, category, index, sliderIndex);
  ++usedIndicatorCount;

  // Переименовать оставшиеся индикаторы чтобы не мешались
  for (indicatorIndex = usedIndicatorCount; indicatorIndex < MAX_INDICATORS; ++indicatorIndex)
  {
    // Тэг элементов интерфейса
    string tagPostfix =  itoa(indicatorIndex);
    string resultBaseTag = "tag_slider_" + itoa(sliderIndex) + "_indicator_" ;
    // Поменять теги элементов
    while(changeLoadingElementTag(tagPostfix, resultBaseTag, ITEM_INDICATOR_MARKET_BASE_TAG))
      ;
  }
}
// Функции авто заполнения данных в UI

```

#### 反

``` c++
slider_black_market_parameters(int slider_black_market_parameters_arg0, int slider_black_market_parameters_arg1)
{
    int slider_black_market_parameters_local0;
    int slider_black_market_parameters_local1;
    int slider_black_market_parameters_local2;
    int slider_black_market_parameters_local3;
    int slider_black_market_parameters_local4;
    string slider_black_market_parameters_local5;
    string slider_black_market_parameters_local6;

    slider_black_market_parameters_local0 = blackMarketCategory(slider_black_market_parameters_arg1);
    // --- Line 205 ---
    // --- Line 206 ---
    slider_black_market_parameters_local1 = blackMarketIndex(slider_black_market_parameters_arg1);
    // --- Line 206 ---
    // --- Line 207 ---
    loadToFrameBySprite(slider_black_market_parameters_arg0, "menus\\frame_empty");
    // --- Line 210 ---
    loadToFrameBySprite(slider_black_market_parameters_arg0, "menus\\frame_black_market_parameters");
    // --- Line 213 ---
    // --- Line 216 ---
    slider_black_market_parameters_local3 = 0;
    // --- Line 216 ---
    // --- Line 217 ---
    for (slider_black_market_parameters_local2 = 0; (slider_black_market_parameters_local2 < 10); (++slider_black_market_parameters_local2)) {
        slider_black_market_parameters_local4 = -999999;
        // --- Line 219 ---
        // --- Line 220 ---
        slider_black_market_parameters_local4 = getEquipmentByCategory(53, slider_black_market_parameters_local0, slider_black_market_parameters_local1, slider_black_market_parameters_local2);
        // --- Line 221 ---
        if ((slider_black_market_parameters_local4 != -999999)) {
        setBlackMarketIndexedParameter(slider_black_market_parameters_local3, slider_black_market_parameters_local4, slider_black_market_parameters_local0, slider_black_market_parameters_local1, slider_black_market_parameters_arg1);
        // --- Line 224 ---
        (++slider_black_market_parameters_local3);
        // --- Line 225 ---
        } else {
        // --- Line 228 ---
        }
    }
    setBlackMarketMajorPerkParameter(slider_black_market_parameters_local3, slider_black_market_parameters_local0, slider_black_market_parameters_local1, slider_black_market_parameters_arg1);
    // --- Line 232 ---
    (++slider_black_market_parameters_local3);
    // --- Line 233 ---
    for (slider_black_market_parameters_local2 = slider_black_market_parameters_local3; (slider_black_market_parameters_local2 < 10); (++slider_black_market_parameters_local2)) {
        slider_black_market_parameters_local5 = itoa(slider_black_market_parameters_local2);
        // --- Line 238 ---
        // --- Line 239 ---
        slider_black_market_parameters_local6 = (("tag_slider_" + itoa(slider_black_market_parameters_arg1)) + "_indicator_");
        // --- Line 239 ---
        // --- Line 240 ---
        // --- Line 243 ---
        while (changeLoadingElementTag(slider_black_market_parameters_local5, slider_black_market_parameters_local6, "tag_indicator_market_")) {
        }
    }
    // return; mark end of function
}

```

### backup

#### 源码

``` c++
```

#### 反

``` c++
```

