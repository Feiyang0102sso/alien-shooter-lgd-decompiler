

## 概述

已修复 是之前做 asm时把字符串按40字符截断导致的

开箱的动画都是没问题的，但是打开箱子左侧物品栏就是全黑的 什么都没有

装备会入库只是不显示

## 调用链

``` 
开盖完成 → startBoxLightAnimation()
         → [光效结束] F3845_14()
         → getNextItemInSupplyBox()      ← 生成物品数据
         → showSupplyItem()              ← ★ 左侧栏主入口
         → selectWeaponaryItemBaseData() ← ★ 左侧图片 + 属性条
```



## showSupplyItem

### 源码

``` c++
// Показать информацию о полученном элементе
showSupplyItem(int supplyType, int category, int index, int quantity, string baseKey, bool isShowLegendaryTutorial = true)
{
  // Загрузка фрейма кнопки
  loadToFrame(BUTTON_FRAME_NVID,  FRAME_BUTTON_OPEN_BOX_NEXT_MENU);

  // Скрыть картинки градации
  setVidDirectionForField(ITEM_GRADE_IMAGE_TAG,   -1, 0);
  // Скрыть картинки качества
  setVidDirectionForField(ITEM_QUALITY_SMALL_IMAGE_TAG, -1, 0);
  setVidDirectionForField(ITEM_QUALITY_IMAGE_TAG, -1, 0);
  
  // Скрыть значения параметров 
  int indicatorIndex;
  int usedIndicatorCount = 0;
  for (indicatorIndex = 0; indicatorIndex < MAX_INDICATORS; ++indicatorIndex)
    hideIndexedParameter(indicatorIndex); 
  
  string typeStr = "";
  string quantityStr = "";
  // Показ содержимого
  if      (supplyType == typeMoney)
  {
    typeStr = GetString("menu", "SupplyGotCredits");
    // Выставить картинку 
    changeImageByTag(ITEM_BIG_IMAGE_TAG, -1, MONEY_BIG_PICTURE_NVID, 0);
    // Выставить количество
    quantityStr = "+" + itoa(quantity);
  }
  else if (supplyType == typeAbility)
  {
    typeStr = GetString("menu", "SupplyGotAmmunition");
    // Выставить картинку 
    setImageForField(ITEM_BIG_IMAGE_TAG, -1, EQUIPMENT_MENU_VID_BIG, category, index);
    // Выставить количество
    quantityStr = "+" + itoa(quantity);
  }
  else if (   (supplyType == typeWeaponTemplate)
          ||  (supplyType == typeArmorTemplate)
          ||  (supplyType == typeHelmTemplate)
          ||  (supplyType == typeBootsTemplate)
          ||  (supplyType == typeDroneTemplate)
          ||  (supplyType == typeImplantTemplate) )
  {
    if        (supplyType == typeWeaponTemplate)
      typeStr = GetString("menu", "SupplyGotWeapon");
    else if   (supplyType == typeArmorTemplate)
      typeStr = GetString("menu", "SupplyGotArmor");
    else if   (supplyType == typeHelmTemplate)
      typeStr = GetString("menu", "SupplyGotHelm");
    else if   (supplyType == typeBootsTemplate)
      typeStr = GetString("menu", "SupplyGotBoots");
    else if   (supplyType == typeDroneTemplate)
      typeStr = GetString("menu", "SupplyGotDrone");
    else if   (supplyType == typeImplantTemplate)
      typeStr = GetString("menu", "SupplyGotImplant");
    
    // Показать информацию о выпавшем предмете
    selectWeaponaryItemBaseData(baseKey);
  }

  // Выставить тип снабжения
  setTextFromString(SUPPLY_TYPE_TEXT_TAG,      typeStr);

  // Выставить выпавшее количество
  setTextFromString(SUPPLY_ITEM_MONEY_TEXT_TAG,     quantityStr);
}


```

### 反编译

``` c++
showSupplyItem(int showSupplyItem_arg0, int showSupplyItem_arg1, int showSupplyItem_arg2, int showSupplyItem_arg3, string showSupplyItem_arg4, int showSupplyItem_arg5 = 1)
{
    int showSupplyItem_local0;
    int showSupplyItem_local1;
    string showSupplyItem_local2;
    string showSupplyItem_local3;

    loadToFrame(597, "menus\\frame_button_open_box_next");
    // --- Line 34 ---
    setVidDirectionForField("tag_item_grade_image", -1, 0);
    // --- Line 37 ---
    setVidDirectionForField("tag_item_quality_small_image", -1, 0);
    // --- Line 39 ---
    setVidDirectionForField("tag_item_quality_image", -1, 0);
    // --- Line 40 ---
    // --- Line 43 ---
    showSupplyItem_local1 = 0;
    // --- Line 43 ---
    // --- Line 44 ---
    for (showSupplyItem_local0 = 0; (showSupplyItem_local0 < 10); (++showSupplyItem_local0)) {
        hideIndexedParameter(showSupplyItem_local0);
        // --- Line 46 ---
    }
    showSupplyItem_local2 = "";
    // --- Line 47 ---
    // --- Line 48 ---
    showSupplyItem_local3 = "";
    // --- Line 48 ---
    // --- Line 49 ---
    if ((showSupplyItem_arg0 == 8)) {
        showSupplyItem_local2 = GetString("menu", "SupplyGotCredits");
        // --- Line 53 ---
        changeImageByTag("tag_big_item_image", -1, 3150, 0);
        // --- Line 55 ---
        showSupplyItem_local3 = ("+" + itoa(showSupplyItem_arg3));
        // --- Line 57 ---
    } else if ((showSupplyItem_arg0 == 108)) {
        showSupplyItem_local2 = GetString("menu", "SupplyGotAmmunition");
        // --- Line 61 ---
        setImageForField("tag_big_item_image", -1, 27, showSupplyItem_arg1, showSupplyItem_arg2);
        // --- Line 63 ---
        showSupplyItem_local3 = ("+" + itoa(showSupplyItem_arg3));
        // --- Line 65 ---
    } else if (((((((showSupplyItem_arg0 == 201) || (showSupplyItem_arg0 == 202)) || (showSupplyItem_arg0 == 203)) || (showSupplyItem_arg0 == 206)) || (showSupplyItem_arg0 == 205)) || (showSupplyItem_arg0 == 204))) {
        if ((showSupplyItem_arg0 == 201)) {
            showSupplyItem_local2 = GetString("menu", "SupplyGotWeapon");
            // --- Line 75 ---
        } else if ((showSupplyItem_arg0 == 202)) {
            showSupplyItem_local2 = GetString("menu", "SupplyGotArmor");
            // --- Line 77 ---
        } else if ((showSupplyItem_arg0 == 203)) {
            showSupplyItem_local2 = GetString("menu", "SupplyGotHelm");
            // --- Line 79 ---
        } else if ((showSupplyItem_arg0 == 206)) {
            showSupplyItem_local2 = GetString("menu", "SupplyGotBoots");
            // --- Line 81 ---
        } else if ((showSupplyItem_arg0 == 205)) {
            showSupplyItem_local2 = GetString("menu", "SupplyGotDrone");
            // --- Line 83 ---
        } else if ((showSupplyItem_arg0 == 204)) {
            showSupplyItem_local2 = GetString("menu", "SupplyGotImplant");
            // --- Line 85 ---
        }
        selectWeaponaryItemBaseData(showSupplyItem_arg4);
        // --- Line 88 ---
    }
    setTextFromString("tag_supply_type_text", showSupplyItem_local2, -1);
    // --- Line 92 ---
    setTextFromString("tag_supply_item_money_text", showSupplyItem_local3, -1);
    // --- Line 95 ---
    // return; mark end of function
}

```



## selectWeaponaryItemBaseData

### 源码

``` c++
selectWeaponaryItemBaseData(string baseKey)
{
  // Получить категорию шаблона модели
  int category = modelCategory(baseKey);
  // Получить индекс шаблона модели (временное хранение)
  int index = modelTemplateIndex(baseKey);

  // Проставить выбранному предмету:
  // большую картинку 
  setImageForField(ITEM_BIG_IMAGE_TAG, -1, EQUIPMENT_MENU_VID_BIG, category, index);
  // описание выбранного элемента
  setImageForField(ITEM_DESCRIPTION_IMAGE_TAG, -1, EQUIPMENT_DESCRIPTION_VID, category, index);
  // качество выбранного элемента
  int qualityLevelIndex = 0;
  if (category != categoryEquip)
  {
    int qualityLevel = getEquipmentByCategory(EQUIPMENT_QUALITY_LEVEL,  category, index);
    qualityLevelIndex = getQualityLevelIndex(qualityLevel);
  }
  int grade = getEquipmentByCategory(EQUIPMENT_GRADE_LEVEL,  category, index);
  setVidDirectionForField(ITEM_GRADE_IMAGE_TAG,   -1, grade);
  setVidDirectionForField(ITEM_QUALITY_IMAGE_TAG, -1, qualityLevelIndex);
  setVidDirectionForField(ITEM_QUALITY_SMALL_IMAGE_TAG, -1, qualityLevelIndex);

  // Показ и скрытие кнопки информации о перках
  if (inventory_activeCategory == categoryEquip)
    setImageVisibility(BUTTON_PERKS_INFO_TAG, -1, false);
  else
    setImageVisibility(BUTTON_PERKS_INFO_TAG, -1, true);

  // Выставить значения параметров 
  int indicatorIndex;
  int usedIndicatorCount = 0;
  for (indicatorIndex = 0; indicatorIndex < MAX_INDICATORS; ++indicatorIndex)
  {
    int indType = getEquipmentByCategory(EQUIPMENT_INDICATOR, category, index, indicatorIndex); 
    if (indType != UNDEFINED_VALUE)
    {
      setIndexedParameter(usedIndicatorCount, indType, baseKey);
      ++usedIndicatorCount;
    }
    else
      hideIndexedParameter(indicatorIndex);
  }

  // Если у модели есть перка - показать её параметры
  if (isModelHavePerks(baseKey))
  {
    // Сгенерировать базовый ключ хранения информации о Перки у модели
    string curPerkBaseKey = modelPerkBaseKey(baseKey, 0);
    // Выставить значение параметра перка для поля соответствующего indType
    setPerkParameter(usedIndicatorCount, curPerkBaseKey);
  }

  // Выставить значения количества выполненных апгрейдов
  int currentUpgrade = modelUpgrade(baseKey);
  int maxUpgrade = getEquipmentByCategory(EQUIPMENT_UPGRADES_COUNT, category, index);
  showUpgradeLevel(maxUpgrade, currentUpgrade); 

  // Обновление состояния панели апгрейда/продажи/кнопок ----------------------------
  if    (isUpgradePanelShown)
  {
    loadToFrame(UPGRADE_INFO_FRAME_NVID,  FRAME_ITEM_INFO_UPGRADE_MENU);

    // Выставить значения параметров апгрейда
    indicatorIndex;
    usedIndicatorCount = 0;
    for (indicatorIndex = 0; indicatorIndex < MAX_INDICATORS; ++indicatorIndex)
    {
      // Тэг элементов интерфейса
      string tag = ITEM_INDICATOR_UPGRADE_BASE_TAG + itoa(indicatorIndex);
      int indType = getEquipmentByCategory(EQUIPMENT_INDICATOR, category, index, indicatorIndex); 
      if (indType != UNDEFINED_VALUE)
      {
        // Выставить значение параметра indicatorIndex для поля соответствующего indType
        setParameterByTag(tag, indType, baseKey, true);
        ++usedIndicatorCount;
      }
      else
        // Скрыть значение параметра
        hideParameterByTag(tag);
    }
  }
  else if (isDismantlePanelShown)
    loadToFrame(UPGRADE_INFO_FRAME_NVID,  FRAME_ITEM_INFO_DISMANTLE_MENU);
  else 
    loadToFrame(UPGRADE_INFO_FRAME_NVID,  FRAME_ITEM_INFO_BUTTONS_MENU);
  // Обновление состояния панели апгрейда/продажи/кнопок ----------------------------
}

```

### 反编译

``` c++
selectWeaponaryItemBaseData(string selectWeaponaryItemBaseData_arg0)
{
    int selectWeaponaryItemBaseData_local0;
    int selectWeaponaryItemBaseData_local1;
    int selectWeaponaryItemBaseData_local2;
    int selectWeaponaryItemBaseData_local3;
    int selectWeaponaryItemBaseData_local4;
    int selectWeaponaryItemBaseData_local5;
    int selectWeaponaryItemBaseData_local6;
    int selectWeaponaryItemBaseData_local7;
    string selectWeaponaryItemBaseData_local8;
    int selectWeaponaryItemBaseData_local9;
    int selectWeaponaryItemBaseData_local10;
    string selectWeaponaryItemBaseData_local11;
    int selectWeaponaryItemBaseData_local12;

    selectWeaponaryItemBaseData_local0 = modelCategory(selectWeaponaryItemBaseData_arg0);
    // --- Line 204 ---
    // --- Line 205 ---
    selectWeaponaryItemBaseData_local1 = modelTemplateIndex(selectWeaponaryItemBaseData_arg0);
    // --- Line 206 ---
    // --- Line 207 ---
    setImageForField("tag_big_item_image", -1, 27, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1);
    // --- Line 211 ---
    setImageForField("tag_item_description_image", -1, 50, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1);
    // --- Line 213 ---
    selectWeaponaryItemBaseData_local2 = 0;
    // --- Line 214 ---
    // --- Line 215 ---
    if ((selectWeaponaryItemBaseData_local0 != 3)) {
        selectWeaponaryItemBaseData_local3 = getEquipmentByCategory(238, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1, -999999);
        // --- Line 217 ---
        // --- Line 218 ---
        selectWeaponaryItemBaseData_local2 = getQualityLevelIndex(selectWeaponaryItemBaseData_local3);
        // --- Line 219 ---
    }
    selectWeaponaryItemBaseData_local4 = getEquipmentByCategory(324, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1, -999999);
    // --- Line 220 ---
    // --- Line 221 ---
    setVidDirectionForField("tag_item_grade_image", -1, selectWeaponaryItemBaseData_local4);
    // --- Line 222 ---
    setVidDirectionForField("tag_item_quality_image", -1, selectWeaponaryItemBaseData_local2);
    // --- Line 223 ---
    setVidDirectionForField("tag_item_quality_small_image", -1, selectWeaponaryItemBaseData_local2);
    // --- Line 224 ---
    if ((inventory_activeCategory == 3)) {
        setImageVisibility("tag_button_perks_info", -1, 0);
        // --- Line 228 ---
    } else {
        setImageVisibility("tag_button_perks_info", -1, 1);
        // --- Line 230 ---
    }
    // --- Line 233 ---
    selectWeaponaryItemBaseData_local6 = 0;
    // --- Line 233 ---
    // --- Line 234 ---
    for (selectWeaponaryItemBaseData_local5 = 0; (selectWeaponaryItemBaseData_local5 < 10); (++selectWeaponaryItemBaseData_local5)) {
        selectWeaponaryItemBaseData_local7 = getEquipmentByCategory(53, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1, selectWeaponaryItemBaseData_local5);
        // --- Line 236 ---
        // --- Line 237 ---
        if ((selectWeaponaryItemBaseData_local7 != -999999)) {
        setIndexedParameter(selectWeaponaryItemBaseData_local6, selectWeaponaryItemBaseData_local7, selectWeaponaryItemBaseData_arg0, 0);
        // --- Line 240 ---
        (++selectWeaponaryItemBaseData_local6);
        // --- Line 241 ---
        } else {
        hideIndexedParameter(selectWeaponaryItemBaseData_local5);
        // --- Line 244 ---
        }
    }
    if (isModelHavePerks(selectWeaponaryItemBaseData_arg0)) {
        selectWeaponaryItemBaseData_local8 = modelPerkBaseKey(selectWeaponaryItemBaseData_arg0, 0);
        // --- Line 250 ---
        // --- Line 251 ---
        setPerkParameter(selectWeaponaryItemBaseData_local6, selectWeaponaryItemBaseData_local8, "");
        // --- Line 253 ---
    }
    selectWeaponaryItemBaseData_local9 = modelUpgrade(selectWeaponaryItemBaseData_arg0);
    // --- Line 256 ---
    // --- Line 257 ---
    selectWeaponaryItemBaseData_local10 = getEquipmentByCategory(11, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1, -999999);
    // --- Line 257 ---
    // --- Line 258 ---
    showUpgradeLevel(selectWeaponaryItemBaseData_local10, selectWeaponaryItemBaseData_local9);
    // --- Line 259 ---
    if (isUpgradePanelShown) {
        loadToFrame(547, "menus\\frame_inventory_item_info_upgrade");
        // --- Line 264 ---
        // WARNING: Orphaned expression -> Stack_Out = selectWeaponaryItemBaseData_local5
        // --- Line 267 ---
        selectWeaponaryItemBaseData_local6 = 0;
        // --- Line 268 ---
        for (selectWeaponaryItemBaseData_local5 = 0; (selectWeaponaryItemBaseData_local5 < 10); (++selectWeaponaryItemBaseData_local5)) {
            selectWeaponaryItemBaseData_local11 = ("tag_indicator_upgrade_" + itoa(selectWeaponaryItemBaseData_local5));
            // --- Line 271 ---
            // --- Line 272 ---
            selectWeaponaryItemBaseData_local12 = getEquipmentByCategory(53, selectWeaponaryItemBaseData_local0, selectWeaponaryItemBaseData_local1, selectWeaponaryItemBaseData_local5);
            // --- Line 272 ---
            // --- Line 273 ---
            if ((selectWeaponaryItemBaseData_local12 != -999999)) {
            setParameterByTag(selectWeaponaryItemBaseData_local11, selectWeaponaryItemBaseData_local12, selectWeaponaryItemBaseData_arg0, 1);
            // --- Line 277 ---
            (++selectWeaponaryItemBaseData_local6);
            // --- Line 278 ---
            } else {
            hideParameterByTag(selectWeaponaryItemBaseData_local11);
            // --- Line 282 ---
            }
        }
    } else if (isDismantlePanelShown) {
        loadToFrame(547, "menus\\frame_inventory_item_info_disma...");
        // --- Line 286 ---
    } else {
        loadToFrame(547, "menus\\frame_inventory_item_info_buttons");
        // --- Line 288 ---
    }
    // return; mark end of function
}

```

## getNextItemInSupplyBox

### 源码

``` c++
// Получить следующий элемент в ящике снабжения
getNextItemInSupplyBox()
{
  int supplyBoxItemsCount = getEquipmentByCategory(EQUIPMENT_SUPPLY_COUNT, supplyBoxCategory, supplyBoxIndex);
//Log("supplyRecievedNumber = " + itoa(supplyRecievedNumber) + ",  from supplyBoxItemsCount = " + itoa(supplyBoxItemsCount));
  if (supplyRecievedNumber >= supplyBoxItemsCount)
    return false;

  ++supplyRecievedNumber;

  string supplyName = getEquipmentByCategory(EQUIPMENT_SUPPLY, supplyBoxCategory, supplyBoxIndex, supplyRecievedNumber - 1);
  int category = categorySupply;
  int index = getEquipmentIndexByName(category, supplyName);
//Log("supplyName = " + supplyName + ",  index = " + itoa(index));
  if (index == UNDEFINED_INDEX)
    return false;

  int supplyRandomVariants = getEquipmentByCategory(EQUIPMENT_RANDOM_SUPPLY_COUNT, category, index);
  if (supplyRandomVariants < 0)
    return false;

  int dempfer = 0;
  // Цикл попыток выкинуть что-то не пустое
  int quantity = 0;
  int supplyType = typeUndefined;
  int supplyIndex = UNDEFINED_INDEX;
  int supplyCategory = categoryUndefined;
  int attemptsCount = 0;
  while ((attemptsCount < MAX_SUPPLY_ATTEMPTS_COUNT) && (supplyIndex == UNDEFINED_INDEX))
  {
    // Увеличить счётчик попыток
    ++attemptsCount;

    // Сгенерировать случайное число в %
    int randomPercentValue = Random(99);

    // Найти выпавший вариант снабжения
    int totalChance = 0;
    int variant;
    for (variant = 0; variant < supplyRandomVariants; ++variant)
    {
      totalChance += getEquipmentByCategory(EQUIPMENT_CHANCE, category, index, variant);
  //Log("variant = " + itoa(variant) + ", chance = " + itoa(getEquipmentByCategory(EQUIPMENT_CHANCE, category, index, variant)) + " totalChance = " + itoa(totalChance));
      if (randomPercentValue < totalChance)
        break;
    }
  //Log("variant = " + itoa(variant) + ", from supplyRandomVariants = " + itoa(supplyRandomVariants));
    if (variant == supplyRandomVariants)
      return false;

    // Сгенерировать случайное количество
    int maxQuantity = getEquipmentByCategory(EQUIPMENT_MAX_QUANTITY,    category, index, variant);
    int minQuantity = getEquipmentByCategory(EQUIPMENT_MIN_QUANTITY,    category, index, variant);
    quantity = minQuantity + Random(maxQuantity - minQuantity);

    supplyType = getEquipmentByCategory(EQUIPMENT_SUPPLY_TYPE,      category, index, variant);
    supplyCategory = getEquipmentByCategory(EQUIPMENT_SUPPLY_CATEGORY, category, index, variant);
    int weaponType = getEquipmentByCategory(EQUIPMENT_WEAPON_TYPE,      category, index, variant);
    int grade = getEquipmentByCategory(EQUIPMENT_GRADE_LEVEL,           category, index, variant);
    int targetQualityLevel = getEquipmentByCategory(EQUIPMENT_QUALITY_LEVEL,  category, index, variant);
    string product = getEquipmentByCategory(EQUIPMENT_BONUS_PRODUCT,    category, index, variant);

    // Experimental main parameters delta dempfer for low quality items 2017-12-07 Sten
    dempfer = (100*Random(qualityLegend - targetQualityLevel)) / qualityLegend;

    if (product == UNDEFINED_STRING_VALUE)
    {
      if      (supplyType == typeMoney)
        supplyIndex = getEquipmentIndexByName(supplyCategory, "VIPmoneypack1");
      else if (supplyType == typeAbility)
        // Получить случайную абилку
        supplyIndex = randomAbilityIndex();
      else if (supplyType == typeWeaponTemplate)
      {
        // Получить случайное оборудование
        supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyWeapon_LevelMaxDelta, supplyWeapon_LevelMinDelta, supplyWeapon_MaxLevel);
        // XXX: Hot fix for PISTOLS AFRTER 10 level! 2017-07-26 Sten
        if ((supplyIndex == UNDEFINED_INDEX) && (weaponType == PISTOL))
        {
          // Получить случайный миниган потому что пистолеты кончились
          weaponType = MINIGUN;
          supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyWeapon_LevelMaxDelta, supplyWeapon_LevelMinDelta, supplyWeapon_MaxLevel);
        }
      }
      else if (supplyType == typeArmorTemplate)
        // Получить случайное оборудование
        supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyArmor_LevelMaxDelta, supplyArmor_LevelMinDelta, supplyArmor_MaxLevel);
      else if (supplyType == typeHelmTemplate)
        // Получить случайное оборудование
        supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyHelm_LevelMaxDelta, supplyHelm_LevelMinDelta, supplyHelm_MaxLevel);
      else if (supplyType == typeBootsTemplate)
        // Получить случайное оборудование
        supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyBoots_LevelMaxDelta, supplyBoots_LevelMinDelta, supplyBoots_MaxLevel);
      else if (supplyType == typeDroneTemplate)
        // Получить случайное оборудование
        supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyDrone_LevelMaxDelta, supplyDrone_LevelMinDelta, supplyDrone_MaxLevel);
      else if (supplyType == typeImplantTemplate)
        // Получить случайное оборудование
        supplyIndex = randomTemlateModel(supplyCategory, supplyType, targetQualityLevel, grade, weaponType, supplyImplant_LevelMaxDelta, supplyImplant_LevelMinDelta, supplyImplant_MaxLevel);
    }
    else
    {
      supplyIndex = getEquipmentIndexByName(supplyCategory, product);
    }
  }

//Log("supplyType = " + itoa(supplyType) + ",  supplyIndex = " + itoa(supplyIndex));

  if (supplyIndex == UNDEFINED_INDEX)
    return false;

  // Вручение содержимого
  string baseKey = UNDEFINED_STRING_VALUE;
  if      (supplyType == typeMoney)
  {
    // Округлить количество полученных монет и начислить их
    quantity -= quantity%supplyGrain_Money;
    increasePlayerMoney(quantity);
  }
  else if (supplyType == typeAbility)
  {
    // Увеличить количество патронов
    addAmmoForWeaponaryItem(supplyCategory, supplyIndex, quantity);
  }
  else if (supplyType == typeWeaponTemplate)
    // Сгенерировать модель по шаблону
    baseKey = generateModelForWeaponTemplate(supplyIndex, dempfer);
  else if (supplyType == typeArmorTemplate)
    // Сгенерировать модель по шаблону
    baseKey = generateModelForArmorTemplate(supplyCategory, supplyIndex, dempfer);
  else if (supplyType == typeHelmTemplate)
    // Сгенерировать модель по шаблону
    baseKey = generateModelForArmorTemplate(supplyCategory, supplyIndex, dempfer);
  else if (supplyType == typeBootsTemplate)
    // Сгенерировать модель по шаблону
    baseKey = generateModelForArmorTemplate(supplyCategory, supplyIndex, dempfer);
  else if (supplyType == typeDroneTemplate)
    // Сгенерировать модель по шаблону
    baseKey = generateModelForDroneTemplate(supplyIndex, dempfer);
  else if (supplyType == typeImplantTemplate)
    // Сгенерировать модель по шаблону
    baseKey = generateModelForImplantTemplate(supplyIndex, dempfer);

  // Показать информацию о полученном элементе
  showSupplyItem(supplyType, supplyCategory, supplyIndex, quantity, baseKey);

  return true;
}


```

### 反编译

``` c++
getNextItemInSupplyBox()
{
    int getNextItemInSupplyBox_local0;
    string getNextItemInSupplyBox_local1;
    int getNextItemInSupplyBox_local2;
    int getNextItemInSupplyBox_local3;
    int getNextItemInSupplyBox_local4;
    int getNextItemInSupplyBox_local5;
    int getNextItemInSupplyBox_local6;
    int getNextItemInSupplyBox_local7;
    int getNextItemInSupplyBox_local8;
    int getNextItemInSupplyBox_local9;
    int getNextItemInSupplyBox_local10;
    int getNextItemInSupplyBox_local11;
    int getNextItemInSupplyBox_local12;
    int getNextItemInSupplyBox_local13;
    int getNextItemInSupplyBox_local14;
    int getNextItemInSupplyBox_local15;
    int getNextItemInSupplyBox_local16;
    int getNextItemInSupplyBox_local17;
    int getNextItemInSupplyBox_local18;
    string getNextItemInSupplyBox_local19;
    string getNextItemInSupplyBox_local20;

    getNextItemInSupplyBox_local0 = getEquipmentByCategory(225, supplyBoxCategory, supplyBoxIndex, -999999);
    // --- Line 197 ---
    // --- Line 198 ---
    if ((supplyRecievedNumber >= getNextItemInSupplyBox_local0)) {
        return 0;
        // --- Line 201 ---
    }
    (++supplyRecievedNumber);
    // --- Line 203 ---
    getNextItemInSupplyBox_local1 = getEquipmentByCategory(226, supplyBoxCategory, supplyBoxIndex, (supplyRecievedNumber - 1));
    // --- Line 204 ---
    // --- Line 205 ---
    getNextItemInSupplyBox_local2 = 21;
    // --- Line 205 ---
    // --- Line 206 ---
    getNextItemInSupplyBox_local3 = getEquipmentIndexByName(getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local1);
    // --- Line 206 ---
    // --- Line 207 ---
    if ((getNextItemInSupplyBox_local3 == -1)) {
        return 0;
        // --- Line 210 ---
    }
    getNextItemInSupplyBox_local4 = getEquipmentByCategory(232, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, -999999);
    // --- Line 211 ---
    // --- Line 212 ---
    if ((getNextItemInSupplyBox_local4 < 0)) {
        return 0;
        // --- Line 214 ---
    }
    getNextItemInSupplyBox_local5 = 0;
    // --- Line 215 ---
    // --- Line 216 ---
    getNextItemInSupplyBox_local6 = 0;
    // --- Line 217 ---
    // --- Line 218 ---
    getNextItemInSupplyBox_local7 = -1;
    // --- Line 218 ---
    // --- Line 219 ---
    getNextItemInSupplyBox_local8 = -1;
    // --- Line 219 ---
    // --- Line 220 ---
    getNextItemInSupplyBox_local9 = -1;
    // --- Line 220 ---
    // --- Line 221 ---
    getNextItemInSupplyBox_local10 = 0;
    // --- Line 221 ---
    // --- Line 222 ---
    while (((getNextItemInSupplyBox_local10 < 10) && (getNextItemInSupplyBox_local8 == -1))) {
        (++getNextItemInSupplyBox_local10);
        // --- Line 226 ---
        getNextItemInSupplyBox_local11 = Random(99);
        // --- Line 228 ---
        // --- Line 229 ---
        getNextItemInSupplyBox_local12 = 0;
        // --- Line 231 ---
        // --- Line 232 ---
        // --- Line 233 ---
        for (getNextItemInSupplyBox_local13 = 0; (getNextItemInSupplyBox_local13 < getNextItemInSupplyBox_local4); (++getNextItemInSupplyBox_local13)) {
            getNextItemInSupplyBox_local12 += getEquipmentByCategory(229, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
            // --- Line 236 ---
            if ((getNextItemInSupplyBox_local11 < getNextItemInSupplyBox_local12)) {
            break;
            }
        }
        if ((getNextItemInSupplyBox_local13 == getNextItemInSupplyBox_local4)) {
            return 0;
            // --- Line 243 ---
        }
        getNextItemInSupplyBox_local14 = getEquipmentByCategory(231, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 245 ---
        // --- Line 246 ---
        getNextItemInSupplyBox_local15 = getEquipmentByCategory(230, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 246 ---
        // --- Line 247 ---
        getNextItemInSupplyBox_local6 = (getNextItemInSupplyBox_local15 + Random((getNextItemInSupplyBox_local14 - getNextItemInSupplyBox_local15)));
        // --- Line 248 ---
        getNextItemInSupplyBox_local7 = getEquipmentByCategory(227, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 250 ---
        getNextItemInSupplyBox_local9 = getEquipmentByCategory(228, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 251 ---
        getNextItemInSupplyBox_local16 = getEquipmentByCategory(109, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 251 ---
        // --- Line 252 ---
        getNextItemInSupplyBox_local17 = getEquipmentByCategory(324, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 252 ---
        // --- Line 253 ---
        getNextItemInSupplyBox_local18 = getEquipmentByCategory(238, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 253 ---
        // --- Line 254 ---
        getNextItemInSupplyBox_local19 = getEquipmentByCategory(98, getNextItemInSupplyBox_local2, getNextItemInSupplyBox_local3, getNextItemInSupplyBox_local13);
        // --- Line 254 ---
        // --- Line 255 ---
        getNextItemInSupplyBox_local5 = ((100 * Random((30 - getNextItemInSupplyBox_local18))) / 30);
        // --- Line 258 ---
        if ((getNextItemInSupplyBox_local19 == "")) {
            if ((getNextItemInSupplyBox_local7 == 8)) {
                getNextItemInSupplyBox_local8 = getEquipmentIndexByName(getNextItemInSupplyBox_local9, "VIPmoneypack1");
                // --- Line 263 ---
            } else if ((getNextItemInSupplyBox_local7 == 108)) {
                getNextItemInSupplyBox_local8 = randomAbilityIndex();
                // --- Line 266 ---
            } else if ((getNextItemInSupplyBox_local7 == 201)) {
                getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 4, 4, 26);
                // --- Line 270 ---
                if (((getNextItemInSupplyBox_local8 == -1) && (getNextItemInSupplyBox_local16 == 1))) {
                    getNextItemInSupplyBox_local16 = 2;
                    // --- Line 275 ---
                    getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 4, 4, 26);
                    // --- Line 276 ---
                }
            } else if ((getNextItemInSupplyBox_local7 == 202)) {
                getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 3, 3, 10);
                // --- Line 281 ---
            } else if ((getNextItemInSupplyBox_local7 == 203)) {
                getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 3, 3, 20);
                // --- Line 284 ---
            } else if ((getNextItemInSupplyBox_local7 == 206)) {
                getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 3, 3, 20);
                // --- Line 287 ---
            } else if ((getNextItemInSupplyBox_local7 == 205)) {
                getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 5, 10, 10);
                // --- Line 290 ---
            } else if ((getNextItemInSupplyBox_local7 == 204)) {
                getNextItemInSupplyBox_local8 = randomTemlateModel(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local18, getNextItemInSupplyBox_local17, getNextItemInSupplyBox_local16, 3, 3, 11);
                // --- Line 293 ---
            }
        } else {
            getNextItemInSupplyBox_local8 = getEquipmentIndexByName(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local19);
            // --- Line 297 ---
        }
    }
    if ((getNextItemInSupplyBox_local8 == -1)) {
        return 0;
        // --- Line 304 ---
    }
    getNextItemInSupplyBox_local20 = "";
    // --- Line 306 ---
    // --- Line 307 ---
    if ((getNextItemInSupplyBox_local7 == 8)) {
        getNextItemInSupplyBox_local6 -= (getNextItemInSupplyBox_local6 % 100);
        // --- Line 311 ---
        increasePlayerMoney(getNextItemInSupplyBox_local6);
        // --- Line 312 ---
    } else if ((getNextItemInSupplyBox_local7 == 108)) {
        addAmmoForWeaponaryItem(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local6);
        // --- Line 317 ---
    } else if ((getNextItemInSupplyBox_local7 == 201)) {
        getNextItemInSupplyBox_local20 = generateModelForWeaponTemplate(getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local5);
        // --- Line 321 ---
    } else if ((getNextItemInSupplyBox_local7 == 202)) {
        getNextItemInSupplyBox_local20 = generateModelForArmorTemplate(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local5);
        // --- Line 324 ---
    } else if ((getNextItemInSupplyBox_local7 == 203)) {
        getNextItemInSupplyBox_local20 = generateModelForArmorTemplate(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local5);
        // --- Line 327 ---
    } else if ((getNextItemInSupplyBox_local7 == 206)) {
        getNextItemInSupplyBox_local20 = generateModelForArmorTemplate(getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local5);
        // --- Line 330 ---
    } else if ((getNextItemInSupplyBox_local7 == 205)) {
        getNextItemInSupplyBox_local20 = generateModelForDroneTemplate(getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local5);
        // --- Line 333 ---
    } else if ((getNextItemInSupplyBox_local7 == 204)) {
        getNextItemInSupplyBox_local20 = generateModelForImplantTemplate(getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local5);
        // --- Line 336 ---
    }
    showSupplyItem(getNextItemInSupplyBox_local7, getNextItemInSupplyBox_local9, getNextItemInSupplyBox_local8, getNextItemInSupplyBox_local6, getNextItemInSupplyBox_local20, 1);
    // --- Line 339 ---
    return 1;
    // --- Line 341 ---
}

```

## startBoxNewItemAnimation

### 源码

``` c++
// Запустить анимацию показа нового предмета
startBoxNewItemAnimation()
{
  loadToFrame(MAIN_OPEN_BOX_REWARD_FRAME_NVID,  FRAME_OPEN_BOX_REWARD);

  int placeHelper = getSpriteByTag(ANIMATION_BOX_ITEM_TAG);
  int animation =   CreateSprite(BOX_ITEM_START_ANIMATION_NVID, ToScreenX(GetX(placeHelper)), ToScreenY(GetY(placeHelper)), GetZ(placeHelper), 0);
  setProportionalScale(animation);
  return true;
}
```



### 反编译

``` c++
startBoxNewItemAnimation()
{
    int startBoxNewItemAnimation_local0;
    int startBoxNewItemAnimation_local1;

    loadToFrame(599, "menus\\frame_confirmations_open_box_re...");
    // --- Line 118 ---
    startBoxNewItemAnimation_local0 = getSpriteByTag("tag_box_item_animation");
    // --- Line 119 ---
    // --- Line 120 ---
    startBoxNewItemAnimation_local1 = CreateSprite(3844, ToScreenX(GetX(startBoxNewItemAnimation_local0)), ToScreenY(GetY(startBoxNewItemAnimation_local0)), GetZ(startBoxNewItemAnimation_local0), 0);
    // --- Line 120 ---
    // --- Line 121 ---
    setProportionalScale(startBoxNewItemAnimation_local1);
    // --- Line 122 ---
    return 1;
    // --- Line 123 ---
}

```

