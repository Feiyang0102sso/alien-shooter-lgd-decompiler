### c

``` c++
fillInventoryShownModels(int fillInventoryShownModels_arg0)
{
    int fillInventoryShownModels_local0;
    int fillInventoryShownModels_local1;
    int fillInventoryShownModels_local2;
    string fillInventoryShownModels_local3;
    string fillInventoryShownModels_local4;
    int fillInventoryShownModels_local5;
    int fillInventoryShownModels_local6;
    int fillInventoryShownModels_local7;
    string fillInventoryShownModels_local8;
    int fillInventoryShownModels_local9;
    string fillInventoryShownModels_local10;
    int fillInventoryShownModels_local11;
    int fillInventoryShownModels_local12;
    string fillInventoryShownModels_local13;
    int fillInventoryShownModels_local14;
    int fillInventoryShownModels_local15;
    int fillInventoryShownModels_local16;
    string fillInventoryShownModels_local17;
    int fillInventoryShownModels_local18;
    string fillInventoryShownModels_local19;
    int fillInventoryShownModels_local20;
    int fillInventoryShownModels_local21;
    int fillInventoryShownModels_local22;
    int fillInventoryShownModels_local23;
    int fillInventoryShownModels_local24;
    int fillInventoryShownModels_local25;
    int fillInventoryShownModels_local26;
    string fillInventoryShownModels_local27;
    int fillInventoryShownModels_local28;
    int fillInventoryShownModels_local29;
    string fillInventoryShownModels_local30;
    int fillInventoryShownModels_local31;
    int fillInventoryShownModels_local32;
    int fillInventoryShownModels_local33;
    int fillInventoryShownModels_local34;
    int fillInventoryShownModels_local35;
    int fillInventoryShownModels_local36;
    int fillInventoryShownModels_local37;
    int fillInventoryShownModels_local38;
    string fillInventoryShownModels_local39;
    int fillInventoryShownModels_local40;
    int fillInventoryShownModels_local41;
    int fillInventoryShownModels_local42;
    string fillInventoryShownModels_local43;
    int fillInventoryShownModels_local44;
    int fillInventoryShownModels_local45;
    int fillInventoryShownModels_local46;
    int fillInventoryShownModels_local47;
    int fillInventoryShownModels_local48;
    string fillInventoryShownModels_local49;
    int fillInventoryShownModels_local50;
    string fillInventoryShownModels_local51;
    int fillInventoryShownModels_local52;
    int fillInventoryShownModels_local53;
    int fillInventoryShownModels_local54;
    int fillInventoryShownModels_local55;
    int fillInventoryShownModels_local56;

    fillInventoryShownModels_local0 = supportedSlotFilter;
    // --- Line 641 ---
    // --- Line 642 ---
    fillInventoryShownModels_local1 = ((infusingItemBaseKey == "null") || (!isShowInfuseVariants));
    // --- Line 642 ---
    // --- Line 643 ---
    if (((!fillInventoryShownModels_local1) && (weaponTypeFilter != 0))) {
        Stack_Out = (fillInventoryShownModels_local0 == -1)
        // --- Line 646 ---
    }
    fillInventoryShownModels_local2 = 1;
    // --- Line 647 ---
    // --- Line 648 ---
    fillInventoryShownModels_local3 = "temp.store_____";
    // --- Line 648 ---
    // --- Line 649 ---
    fillInventoryShownModels_local4 = "temp.store_____";
    // --- Line 649 ---
    // --- Line 650 ---
    if (isMerchantInited) {
        if ((merchantMode == 0)) {
            fillInventoryShownModels_local3 = "store_global_merchant";
            // --- Line 655 ---
            if ((fillInventoryShownModels_arg0 == 5)) {
                fillInventoryShownModels_arg0 = 0;
                // --- Line 657 ---
            }
        } else if ((fillInventoryShownModels_arg0 == 5)) {
            fillInventoryShownModels_local3 = "store_backpack";
            // --- Line 660 ---
        } else if ((merchantMode == 1)) {
            fillInventoryShownModels_local3 = "store_inventory";
            // --- Line 662 ---
        }
        if ((merchantMode == 1)) {
            fillInventoryShownModels_local2 = 1;
            // --- Line 665 ---
        }
    } else if ((fillInventoryShownModels_arg0 == 5)) {
        fillInventoryShownModels_local3 = "store_backpack";
        // --- Line 668 ---
    } else if ((fillInventoryShownModels_arg0 == 8)) {
        fillInventoryShownModels_local3 = "store_inventory";
        // --- Line 674 ---
    } else if ((fillInventoryShownModels_arg0 == 9)) {
        fillInventoryShownModels_local3 = "store_inventory";
        // --- Line 676 ---
    } else if (isShowInfuseVariants) {
        fillInventoryShownModels_local4 = "store_inventory";
        // --- Line 678 ---
    } else {
        fillInventoryShownModels_local3 = "store_equiped";
        // --- Line 681 ---
        fillInventoryShownModels_local4 = "store_inventory";
        // --- Line 682 ---
    }
    inventoryShownModelsNumbersCount = 0;
    // --- Line 687 ---
    fillInventoryShownModels_local5 = 0;
    // --- Line 688 ---
    // --- Line 689 ---
    if ((fillInventoryShownModels_arg0 == 1)) {
        fillInventoryShownModels_local5 = 39;
        // --- Line 691 ---
    } else if ((fillInventoryShownModels_arg0 == 3)) {
        fillInventoryShownModels_local5 = 42;
        // --- Line 693 ---
    } else if ((fillInventoryShownModels_arg0 == 4)) {
        fillInventoryShownModels_local5 = 43;
        // --- Line 695 ---
    } else if ((fillInventoryShownModels_arg0 == 10)) {
        fillInventoryShownModels_local5 = 80;
        // --- Line 697 ---
    } else if ((fillInventoryShownModels_arg0 == 11)) {
        fillInventoryShownModels_local5 = 81;
        // --- Line 699 ---
    }
    if (((((fillInventoryShownModels_arg0 == 0) || (fillInventoryShownModels_arg0 == 5)) || (fillInventoryShownModels_arg0 == 8)) || (fillInventoryShownModels_arg0 == 6))) {
        fillInventoryShownModels_local6 = modelCount(fillInventoryShownModels_local3);
        // --- Line 708 ---
        // --- Line 709 ---
        // --- Line 710 ---
        for (fillInventoryShownModels_local7 = 0; (fillInventoryShownModels_local7 < fillInventoryShownModels_local6); (++fillInventoryShownModels_local7)) {
            fillInventoryShownModels_local8 = modelBaseKey(fillInventoryShownModels_local3, fillInventoryShownModels_local7);
            // --- Line 713 ---
            // --- Line 714 ---
            if (((!isModelEmpty(fillInventoryShownModels_local8)) && (modelLight(fillInventoryShownModels_local8) > lightFilterValue))) {
            fillInventoryShownModels_local9 = modelCategory(fillInventoryShownModels_local8);
            // --- Line 717 ---
            // --- Line 718 ---
            if ((fillInventoryShownModels_local2 || ((fillInventoryShownModels_local9 != 74) && (fillInventoryShownModels_local9 != 76)))) {
            inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local8;
            // --- Line 721 ---
            (++inventoryShownModelsNumbersCount);
            // --- Line 722 ---
            }
            }
        }
        fillInventoryShownModels_local6 = modelCount(fillInventoryShownModels_local4);
        // --- Line 729 ---
        for (fillInventoryShownModels_local7 = 0; (fillInventoryShownModels_local7 < fillInventoryShownModels_local6); (++fillInventoryShownModels_local7)) {
            fillInventoryShownModels_local10 = modelBaseKey(fillInventoryShownModels_local4, fillInventoryShownModels_local7);
            // --- Line 732 ---
            // --- Line 733 ---
            if (((!isModelEmpty(fillInventoryShownModels_local10)) && (modelLight(fillInventoryShownModels_local10) > lightFilterValue))) {
            inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local10;
            // --- Line 737 ---
            (++inventoryShownModelsNumbersCount);
            // --- Line 738 ---
            }
        }
    } else if ((fillInventoryShownModels_arg0 == 9)) {
        fillInventoryShownModels_local11 = modelCount(fillInventoryShownModels_local3);
        // --- Line 745 ---
        // --- Line 746 ---
        // --- Line 747 ---
        for (fillInventoryShownModels_local12 = 0; (fillInventoryShownModels_local12 < fillInventoryShownModels_local11); (++fillInventoryShownModels_local12)) {
            fillInventoryShownModels_local13 = modelBaseKey(fillInventoryShownModels_local3, fillInventoryShownModels_local12);
            // --- Line 750 ---
            // --- Line 751 ---
            if ((!isModelEmpty(fillInventoryShownModels_local13))) {
            fillInventoryShownModels_local14 = modelCategory(fillInventoryShownModels_local13);
            // --- Line 755 ---
            // --- Line 756 ---
            if ((((fillInventoryShownModels_local14 != 74) && (fillInventoryShownModels_local14 != 76)) && (fillInventoryShownModels_local14 != 80))) {
            inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local13;
            // --- Line 759 ---
            (++inventoryShownModelsNumbersCount);
            // --- Line 760 ---
            }
            }
        }
    } else if ((fillInventoryShownModels_arg0 == 2)) {
        fillInventoryShownModels_local15 = modelCount(fillInventoryShownModels_local3);
        // --- Line 769 ---
        // --- Line 770 ---
        // --- Line 771 ---
        if (fillInventoryShownModels_local1) {
            for (fillInventoryShownModels_local16 = 0; (fillInventoryShownModels_local16 < fillInventoryShownModels_local15); (++fillInventoryShownModels_local16)) {
                fillInventoryShownModels_local17 = modelBaseKey(fillInventoryShownModels_local3, fillInventoryShownModels_local16);
                // --- Line 776 ---
                // --- Line 777 ---
                if ((!isModelEmpty(fillInventoryShownModels_local17))) {
                fillInventoryShownModels_local18 = modelCategory(fillInventoryShownModels_local17);
                // --- Line 781 ---
                // --- Line 782 ---
                if ((((fillInventoryShownModels_local18 == 40) || (fillInventoryShownModels_local18 == 47)) || (fillInventoryShownModels_local18 == 41))) {
                if (((armorCategoryFilter == 0) || (fillInventoryShownModels_local18 == armorCategoryFilter))) {
                inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local17;
                // --- Line 787 ---
                (++inventoryShownModelsNumbersCount);
                // --- Line 788 ---
                }
                }
                }
            }
        }
        fillInventoryShownModels_local15 = modelCount(fillInventoryShownModels_local4);
        // --- Line 797 ---
        for (fillInventoryShownModels_local16 = 0; (fillInventoryShownModels_local16 < fillInventoryShownModels_local15); (++fillInventoryShownModels_local16)) {
            fillInventoryShownModels_local19 = modelBaseKey(fillInventoryShownModels_local4, fillInventoryShownModels_local16);
            // --- Line 800 ---
            // --- Line 801 ---
            if (((!isModelEmpty(fillInventoryShownModels_local19)) && (modelLight(fillInventoryShownModels_local19) > lightFilterValue))) {
            fillInventoryShownModels_local20 = modelCategory(fillInventoryShownModels_local19);
            // --- Line 805 ---
            // --- Line 806 ---
            if ((((fillInventoryShownModels_local20 == 40) || (fillInventoryShownModels_local20 == 47)) || (fillInventoryShownModels_local20 == 41))) {
            if (((armorCategoryFilter == 0) || (fillInventoryShownModels_local20 == armorCategoryFilter))) {
            fillInventoryShownModels_local21 = 1;
            // --- Line 810 ---
            // --- Line 811 ---
            if ((!fillInventoryShownModels_local1)) {
            fillInventoryShownModels_local22 = modelTemplateIndex(fillInventoryShownModels_local19);
            // --- Line 814 ---
            // --- Line 815 ---
            fillInventoryShownModels_local23 = getEquipmentByCategory(238, fillInventoryShownModels_local20, fillInventoryShownModels_local22, -999999);
            // --- Line 815 ---
            // --- Line 816 ---
            fillInventoryShownModels_local24 = getEquipmentByCategory(324, fillInventoryShownModels_local20, fillInventoryShownModels_local22, -999999);
            // --- Line 816 ---
            // --- Line 817 ---
            fillInventoryShownModels_local21 = (((fillInventoryShownModels_local23 > 0) && (fillInventoryShownModels_local23 < 30)) && (fillInventoryShownModels_local24 != 11));
            // --- Line 818 ---
            if (fillInventoryShownModels_local21) {
            if (isModelInAnySet(fillInventoryShownModels_local19)) {
            fillInventoryShownModels_local21 = 0;
            // --- Line 822 ---
            }
            }
            }
            if (fillInventoryShownModels_local21) {
            inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local19;
            // --- Line 827 ---
            (++inventoryShownModelsNumbersCount);
            // --- Line 828 ---
            }
            }
            }
            }
        }
    } else if ((fillInventoryShownModels_arg0 == 1)) {
        fillInventoryShownModels_local25 = modelCount(fillInventoryShownModels_local3);
        // --- Line 839 ---
        // --- Line 840 ---
        // --- Line 841 ---
        if (fillInventoryShownModels_local1) {
            for (fillInventoryShownModels_local26 = 0; (fillInventoryShownModels_local26 < fillInventoryShownModels_local25); (++fillInventoryShownModels_local26)) {
                fillInventoryShownModels_local27 = modelBaseKey(fillInventoryShownModels_local3, fillInventoryShownModels_local26);
                // --- Line 846 ---
                // --- Line 847 ---
                if ((!isModelEmpty(fillInventoryShownModels_local27))) {
                fillInventoryShownModels_local28 = modelCategory(fillInventoryShownModels_local27);
                // --- Line 851 ---
                // --- Line 852 ---
                if ((fillInventoryShownModels_local28 == 39)) {
                fillInventoryShownModels_local29 = modelTemplateIndex(fillInventoryShownModels_local27);
                // --- Line 855 ---
                // --- Line 856 ---
                if (((weaponTypeFilter == 0) || (weaponTypeFilter == getEquipmentByCategory(109, fillInventoryShownModels_local28, fillInventoryShownModels_local29, -999999)))) {
                if (((fillInventoryShownModels_local0 == -1) || (fillInventoryShownModels_local0 == getEquipmentByCategory(542, fillInventoryShownModels_local28, fillInventoryShownModels_local29, -999999)))) {
                inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local27;
                // --- Line 861 ---
                (++inventoryShownModelsNumbersCount);
                // --- Line 862 ---
                }
                }
                }
                }
            }
        }
        fillInventoryShownModels_local25 = modelCount(fillInventoryShownModels_local4);
        // --- Line 872 ---
        for (fillInventoryShownModels_local26 = 0; (fillInventoryShownModels_local26 < fillInventoryShownModels_local25); (++fillInventoryShownModels_local26)) {
            fillInventoryShownModels_local30 = modelBaseKey(fillInventoryShownModels_local4, fillInventoryShownModels_local26);
            // --- Line 875 ---
            // --- Line 876 ---
            if (((!isModelEmpty(fillInventoryShownModels_local30)) && (modelLight(fillInventoryShownModels_local30) > lightFilterValue))) {
            fillInventoryShownModels_local31 = modelCategory(fillInventoryShownModels_local30);
            // --- Line 880 ---
            // --- Line 881 ---
            if ((fillInventoryShownModels_local31 == 39)) {
            fillInventoryShownModels_local32 = modelTemplateIndex(fillInventoryShownModels_local30);
            // --- Line 884 ---
            // --- Line 885 ---
            if (((weaponTypeFilter == 0) || (weaponTypeFilter == getEquipmentByCategory(109, fillInventoryShownModels_local31, fillInventoryShownModels_local32, -999999)))) {
            if (((fillInventoryShownModels_local0 == -1) || (fillInventoryShownModels_local0 == getEquipmentByCategory(542, fillInventoryShownModels_local31, fillInventoryShownModels_local32, -999999)))) {
            fillInventoryShownModels_local33 = 1;
            // --- Line 889 ---
            // --- Line 890 ---
            if ((!fillInventoryShownModels_local1)) {
            fillInventoryShownModels_local34 = getEquipmentByCategory(238, fillInventoryShownModels_local31, fillInventoryShownModels_local32, -999999);
            // --- Line 892 ---
            // --- Line 893 ---
            fillInventoryShownModels_local35 = getEquipmentByCategory(324, fillInventoryShownModels_local31, fillInventoryShownModels_local32, -999999);
            // --- Line 893 ---
            // --- Line 894 ---
            fillInventoryShownModels_local33 = (((fillInventoryShownModels_local34 > 0) && (fillInventoryShownModels_local34 < 30)) && (fillInventoryShownModels_local35 != 11));
            // --- Line 895 ---
            if (fillInventoryShownModels_local33) {
            if (isModelInAnySet(fillInventoryShownModels_local30)) {
            fillInventoryShownModels_local33 = 0;
            // --- Line 899 ---
            }
            }
            }
            if (fillInventoryShownModels_local33) {
            inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local30;
            // --- Line 904 ---
            (++inventoryShownModelsNumbersCount);
            // --- Line 905 ---
            }
            }
            }
            }
            }
        }
    } else if ((fillInventoryShownModels_arg0 == 7)) {
        fillInventoryShownModels_local36 = 0;
        // --- Line 916 ---
        // --- Line 917 ---
        if (isState("temp.action.open.legendary.inventory", 1)) {
            stateRemove("temp.action.open.legendary.inventory");
            // --- Line 921 ---
            fillInventoryShownModels_local36 = 1;
            // --- Line 922 ---
        }
        fillInventoryShownModels_local37 = modelCount(fillInventoryShownModels_local3);
        // --- Line 925 ---
        // --- Line 926 ---
        // --- Line 927 ---
        if (fillInventoryShownModels_local1) {
            for (fillInventoryShownModels_local38 = 0; (fillInventoryShownModels_local38 < fillInventoryShownModels_local37); (++fillInventoryShownModels_local38)) {
                fillInventoryShownModels_local39 = modelBaseKey(fillInventoryShownModels_local3, fillInventoryShownModels_local38);
                // --- Line 932 ---
                // --- Line 933 ---
                if ((!isModelEmpty(fillInventoryShownModels_local39))) {
                fillInventoryShownModels_local40 = modelCategory(fillInventoryShownModels_local39);
                // --- Line 937 ---
                // --- Line 938 ---
                if ((fillInventoryShownModels_local40 != 80)) {
                fillInventoryShownModels_local41 = modelTemplateIndex(fillInventoryShownModels_local39);
                // --- Line 941 ---
                // --- Line 942 ---
                fillInventoryShownModels_local42 = getEquipmentByCategory(238, fillInventoryShownModels_local40, fillInventoryShownModels_local41, -999999);
                // --- Line 942 ---
                // --- Line 943 ---
                if ((fillInventoryShownModels_local42 >= 30)) {
                if (fillInventoryShownModels_local36) {
                if ((isModelNew(fillInventoryShownModels_local39) || (modelUpgrade(fillInventoryShownModels_local39) < modelPendingUpgrade(fillInventoryShownModels_local39)))) {
                inventory_selectedSliderIndex = inventoryShownModelsNumbersCount;
                // --- Line 949 ---
                fillInventoryShownModels_local36 = 0;
                // --- Line 950 ---
                }
                }
                inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local39;
                // --- Line 953 ---
                (++inventoryShownModelsNumbersCount);
                // --- Line 954 ---
                }
                }
                }
            }
        }
        fillInventoryShownModels_local37 = modelCount(fillInventoryShownModels_local4);
        // --- Line 963 ---
        if (fillInventoryShownModels_local1) {
            for (fillInventoryShownModels_local38 = 0; (fillInventoryShownModels_local38 < fillInventoryShownModels_local37); (++fillInventoryShownModels_local38)) {
                fillInventoryShownModels_local43 = modelBaseKey(fillInventoryShownModels_local4, fillInventoryShownModels_local38);
                // --- Line 968 ---
                // --- Line 969 ---
                if ((!isModelEmpty(fillInventoryShownModels_local43))) {
                fillInventoryShownModels_local44 = modelCategory(fillInventoryShownModels_local43);
                // --- Line 973 ---
                // --- Line 974 ---
                if ((fillInventoryShownModels_local44 != 80)) {
                fillInventoryShownModels_local45 = modelTemplateIndex(fillInventoryShownModels_local43);
                // --- Line 977 ---
                // --- Line 978 ---
                fillInventoryShownModels_local46 = getEquipmentByCategory(238, fillInventoryShownModels_local44, fillInventoryShownModels_local45, -999999);
                // --- Line 978 ---
                // --- Line 979 ---
                if ((fillInventoryShownModels_local46 >= 30)) {
                if (fillInventoryShownModels_local36) {
                if ((isModelNew(fillInventoryShownModels_local43) || (modelUpgrade(fillInventoryShownModels_local43) < modelPendingUpgrade(fillInventoryShownModels_local43)))) {
                inventory_selectedSliderIndex = inventoryShownModelsNumbersCount;
                // --- Line 985 ---
                fillInventoryShownModels_local36 = 0;
                // --- Line 986 ---
                }
                }
                inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local43;
                // --- Line 989 ---
                (++inventoryShownModelsNumbersCount);
                // --- Line 990 ---
                }
                }
                }
            }
        }
    } else {
        fillInventoryShownModels_local47 = modelCount(fillInventoryShownModels_local3);
        // --- Line 1000 ---
        // --- Line 1001 ---
        // --- Line 1002 ---
        if (fillInventoryShownModels_local1) {
            for (fillInventoryShownModels_local48 = 0; (fillInventoryShownModels_local48 < fillInventoryShownModels_local47); (++fillInventoryShownModels_local48)) {
                fillInventoryShownModels_local49 = modelBaseKey(fillInventoryShownModels_local3, fillInventoryShownModels_local48);
                // --- Line 1007 ---
                // --- Line 1008 ---
                if ((!isModelEmpty(fillInventoryShownModels_local49))) {
                fillInventoryShownModels_local50 = modelCategory(fillInventoryShownModels_local49);
                // --- Line 1012 ---
                // --- Line 1013 ---
                if (((fillInventoryShownModels_local50 == fillInventoryShownModels_local5) && (modelLight(fillInventoryShownModels_local49) > lightFilterValue))) {
                if (((fillInventoryShownModels_local0 == -1) || (fillInventoryShownModels_local0 == getEquipmentByCategory(542, fillInventoryShownModels_local50, modelTemplateIndex(fillInventoryShownModels_local49), -999999)))) {
                inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local49;
                // --- Line 1018 ---
                (++inventoryShownModelsNumbersCount);
                // --- Line 1019 ---
                }
                }
                }
            }
        }
        fillInventoryShownModels_local47 = modelCount(fillInventoryShownModels_local4);
        // --- Line 1028 ---
        for (fillInventoryShownModels_local48 = 0; (fillInventoryShownModels_local48 < fillInventoryShownModels_local47); (++fillInventoryShownModels_local48)) {
            fillInventoryShownModels_local51 = modelBaseKey(fillInventoryShownModels_local4, fillInventoryShownModels_local48);
            // --- Line 1031 ---
            // --- Line 1032 ---
            if (((!isModelEmpty(fillInventoryShownModels_local51)) && (modelLight(fillInventoryShownModels_local51) > lightFilterValue))) {
            fillInventoryShownModels_local52 = modelCategory(fillInventoryShownModels_local51);
            // --- Line 1036 ---
            // --- Line 1037 ---
            if (((fillInventoryShownModels_local52 == fillInventoryShownModels_local5) && (modelLight(fillInventoryShownModels_local51) >= lightFilterValue))) {
            if (((fillInventoryShownModels_local0 == -1) || (fillInventoryShownModels_local0 == getEquipmentByCategory(542, fillInventoryShownModels_local52, modelTemplateIndex(fillInventoryShownModels_local51), -999999)))) {
            fillInventoryShownModels_local53 = 1;
            // --- Line 1041 ---
            // --- Line 1042 ---
            if ((!fillInventoryShownModels_local1)) {
            fillInventoryShownModels_local54 = modelTemplateIndex(fillInventoryShownModels_local51);
            // --- Line 1045 ---
            // --- Line 1046 ---
            fillInventoryShownModels_local55 = getEquipmentByCategory(238, fillInventoryShownModels_local52, fillInventoryShownModels_local54, -999999);
            // --- Line 1046 ---
            // --- Line 1047 ---
            fillInventoryShownModels_local56 = getEquipmentByCategory(324, fillInventoryShownModels_local52, fillInventoryShownModels_local54, -999999);
            // --- Line 1047 ---
            // --- Line 1048 ---
            fillInventoryShownModels_local53 = (((fillInventoryShownModels_local55 > 0) && (fillInventoryShownModels_local55 < 30)) && (fillInventoryShownModels_local56 != 11));
            // --- Line 1049 ---
            if (fillInventoryShownModels_local53) {
            if (isModelInAnySet(fillInventoryShownModels_local51)) {
            fillInventoryShownModels_local53 = 0;
            // --- Line 1053 ---
            }
            }
            }
            if (fillInventoryShownModels_local53) {
            inventoryShownModels[inventoryShownModelsNumbersCount] = fillInventoryShownModels_local51;
            // --- Line 1058 ---
            (++inventoryShownModelsNumbersCount);
            // --- Line 1059 ---
            }
            }
            }
            }
        }
    }
    // return; mark end of function
}

```
### asm

``` assembly
;Function fillInventoryShownModels() Begin
  142E3A:  24 2E 5C 00 00     PUSH_VAR     supportedSlotFilter
  142E3F:  26 AA 5C 00 00     ASSIGN       fillInventoryShownModels_local0
  142E44:  19 81 02 00 00     LINE_NUM     641               ; Code Line 641
  142E49:  19 82 02 00 00     LINE_NUM     642               ; Code Line 642
  142E4E:  24 31 5C 00 00     PUSH_VAR     infusingItemBaseKey
  142E53:  02 6E 75 6C 6C 00  PUSH_STR     "null"
  142E59:  0D                 EQ           
  142E5A:  2D 0B 00 00 00     OR_JMP       loc_142E66        ; Rel: +0xB
  142E5F:  24 58 54 00 00     PUSH_VAR     isShowInfuseVariants
  142E64:  05                 LOG_NOT      
  142E65:  0E                 LOG_OR       
loc_142E66:
  142E66:  26 AB 5C 00 00     ASSIGN       fillInventoryShownModels_local1
  142E6B:  19 82 02 00 00     LINE_NUM     642               ; Code Line 642
  142E70:  19 83 02 00 00     LINE_NUM     643               ; Code Line 643
  142E75:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  142E7A:  05                 LOG_NOT      
  142E7B:  2C 10 00 00 00     AND_JMP      loc_142E8C        ; Rel: +0x10
  142E80:  24 2F 5C 00 00     PUSH_VAR     weaponTypeFilter
  142E85:  01 00 00 00 00     PUSH_INT     0
  142E8A:  14                 NE           
  142E8B:  15                 LOG_AND      
loc_142E8C:
  142E8C:  18 14 00 00 00     JMP_FALSE    loc_142EA1        ; Rel: +0x14
  142E91:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  142E96:  01 FF FF FF FF     PUSH_INT     -1
  142E9B:  0D                 EQ           
  142E9C:  19 86 02 00 00     LINE_NUM     646               ; Code Line 646
loc_142EA1:
  142EA1:  01 01 00 00 00     PUSH_INT     1
  142EA6:  26 AC 5C 00 00     ASSIGN       fillInventoryShownModels_local2
  142EAB:  19 87 02 00 00     LINE_NUM     647               ; Code Line 647
  142EB0:  19 88 02 00 00     LINE_NUM     648               ; Code Line 648
  142EB5:  02 74 65 6D 70 2E  PUSH_STR     "temp.store_____"
        73 74 6F 72 65 5F
        5F 5F 5F 5F 00
  142EC6:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  142ECB:  19 88 02 00 00     LINE_NUM     648               ; Code Line 648
  142ED0:  19 89 02 00 00     LINE_NUM     649               ; Code Line 649
  142ED5:  02 74 65 6D 70 2E  PUSH_STR     "temp.store_____"
        73 74 6F 72 65 5F
        5F 5F 5F 5F 00
  142EE6:  26 AE 5C 00 00     ASSIGN       fillInventoryShownModels_local4
  142EEB:  19 89 02 00 00     LINE_NUM     649               ; Code Line 649
  142EF0:  19 8A 02 00 00     LINE_NUM     650               ; Code Line 650
  142EF5:  24 52 54 00 00     PUSH_VAR     isMerchantInited
  142EFA:  18 D7 00 00 00     JMP_FALSE    loc_142FD2        ; Rel: +0xD7
  142EFF:  24 55 54 00 00     PUSH_VAR     merchantMode
  142F04:  01 00 00 00 00     PUSH_INT     0
  142F09:  0D                 EQ           
  142F0A:  18 49 00 00 00     JMP_FALSE    loc_142F54        ; Rel: +0x49
  142F0F:  02 73 74 6F 72 65  PUSH_STR     "store_global_merchant"
        5F 67 6C 6F 62 61
        6C 5F 6D 65 72 63
        68 61 6E 74 00
  142F26:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  142F2B:  19 8F 02 00 00     LINE_NUM     655               ; Code Line 655
  142F30:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  142F35:  01 05 00 00 00     PUSH_INT     5
  142F3A:  0D                 EQ           
  142F3B:  18 13 00 00 00     JMP_FALSE    loc_142F4F        ; Rel: +0x13
  142F40:  01 00 00 00 00     PUSH_INT     0
  142F45:  26 A9 5C 00 00     ASSIGN       fillInventoryShownModels_arg0
  142F4A:  19 91 02 00 00     LINE_NUM     657               ; Code Line 657
loc_142F4F:
  142F4F:  1C 5E 00 00 00     JMP          loc_142FAE        ; Rel: +0x5E
loc_142F54:
  142F54:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  142F59:  01 05 00 00 00     PUSH_INT     5
  142F5E:  0D                 EQ           
  142F5F:  18 23 00 00 00     JMP_FALSE    loc_142F83        ; Rel: +0x23
  142F64:  02 73 74 6F 72 65  PUSH_STR     "store_backpack"
        5F 62 61 63 6B 70
        61 63 6B 00
  142F74:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  142F79:  19 94 02 00 00     LINE_NUM     660               ; Code Line 660
  142F7E:  1C 2F 00 00 00     JMP          loc_142FAE        ; Rel: +0x2F
loc_142F83:
  142F83:  24 55 54 00 00     PUSH_VAR     merchantMode
  142F88:  01 01 00 00 00     PUSH_INT     1
  142F8D:  0D                 EQ           
  142F8E:  18 1F 00 00 00     JMP_FALSE    loc_142FAE        ; Rel: +0x1F
  142F93:  02 73 74 6F 72 65  PUSH_STR     "store_inventory"
        5F 69 6E 76 65 6E
        74 6F 72 79 00
  142FA4:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  142FA9:  19 96 02 00 00     LINE_NUM     662               ; Code Line 662
loc_142FAE:
  142FAE:  24 55 54 00 00     PUSH_VAR     merchantMode
  142FB3:  01 01 00 00 00     PUSH_INT     1
  142FB8:  0D                 EQ           
  142FB9:  18 13 00 00 00     JMP_FALSE    loc_142FCD        ; Rel: +0x13
  142FBE:  01 01 00 00 00     PUSH_INT     1
  142FC3:  26 AC 5C 00 00     ASSIGN       fillInventoryShownModels_local2
  142FC8:  19 99 02 00 00     LINE_NUM     665               ; Code Line 665
loc_142FCD:
  142FCD:  1C F1 00 00 00     JMP          loc_1430BF        ; Rel: +0xF1
loc_142FD2:
  142FD2:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  142FD7:  01 05 00 00 00     PUSH_INT     5
  142FDC:  0D                 EQ           
  142FDD:  18 23 00 00 00     JMP_FALSE    loc_143001        ; Rel: +0x23
  142FE2:  02 73 74 6F 72 65  PUSH_STR     "store_backpack"
        5F 62 61 63 6B 70
        61 63 6B 00
  142FF2:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  142FF7:  19 9C 02 00 00     LINE_NUM     668               ; Code Line 668
  142FFC:  1C C2 00 00 00     JMP          loc_1430BF        ; Rel: +0xC2
loc_143001:
  143001:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  143006:  01 08 00 00 00     PUSH_INT     8
  14300B:  0D                 EQ           
  14300C:  18 24 00 00 00     JMP_FALSE    loc_143031        ; Rel: +0x24
  143011:  02 73 74 6F 72 65  PUSH_STR     "store_inventory"
        5F 69 6E 76 65 6E
        74 6F 72 79 00
  143022:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  143027:  19 A2 02 00 00     LINE_NUM     674               ; Code Line 674
  14302C:  1C 92 00 00 00     JMP          loc_1430BF        ; Rel: +0x92
loc_143031:
  143031:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  143036:  01 09 00 00 00     PUSH_INT     9
  14303B:  0D                 EQ           
  14303C:  18 24 00 00 00     JMP_FALSE    loc_143061        ; Rel: +0x24
  143041:  02 73 74 6F 72 65  PUSH_STR     "store_inventory"
        5F 69 6E 76 65 6E
        74 6F 72 79 00
  143052:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  143057:  19 A4 02 00 00     LINE_NUM     676               ; Code Line 676
  14305C:  1C 62 00 00 00     JMP          loc_1430BF        ; Rel: +0x62
loc_143061:
  143061:  24 58 54 00 00     PUSH_VAR     isShowInfuseVariants
  143066:  18 24 00 00 00     JMP_FALSE    loc_14308B        ; Rel: +0x24
  14306B:  02 73 74 6F 72 65  PUSH_STR     "store_inventory"
        5F 69 6E 76 65 6E
        74 6F 72 79 00
  14307C:  26 AE 5C 00 00     ASSIGN       fillInventoryShownModels_local4
  143081:  19 A6 02 00 00     LINE_NUM     678               ; Code Line 678
  143086:  1C 38 00 00 00     JMP          loc_1430BF        ; Rel: +0x38
loc_14308B:
  14308B:  02 73 74 6F 72 65  PUSH_STR     "store_equiped"
        5F 65 71 75 69 70
        65 64 00
  14309A:  26 AD 5C 00 00     ASSIGN       fillInventoryShownModels_local3
  14309F:  19 A9 02 00 00     LINE_NUM     681               ; Code Line 681
  1430A4:  02 73 74 6F 72 65  PUSH_STR     "store_inventory"
        5F 69 6E 76 65 6E
        74 6F 72 79 00
  1430B5:  26 AE 5C 00 00     ASSIGN       fillInventoryShownModels_local4
  1430BA:  19 AA 02 00 00     LINE_NUM     682               ; Code Line 682
loc_1430BF:
  1430BF:  01 00 00 00 00     PUSH_INT     0
  1430C4:  26 2C 5C 00 00     ASSIGN       inventoryShownModelsNumbersCount
  1430C9:  19 AF 02 00 00     LINE_NUM     687               ; Code Line 687
  1430CE:  01 00 00 00 00     PUSH_INT     0
  1430D3:  26 AF 5C 00 00     ASSIGN       fillInventoryShownModels_local5
  1430D8:  19 B0 02 00 00     LINE_NUM     688               ; Code Line 688
  1430DD:  19 B1 02 00 00     LINE_NUM     689               ; Code Line 689
  1430E2:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1430E7:  01 01 00 00 00     PUSH_INT     1
  1430EC:  0D                 EQ           
  1430ED:  18 18 00 00 00     JMP_FALSE    loc_143106        ; Rel: +0x18
  1430F2:  01 27 00 00 00     PUSH_INT     39
  1430F7:  26 AF 5C 00 00     ASSIGN       fillInventoryShownModels_local5
  1430FC:  19 B3 02 00 00     LINE_NUM     691               ; Code Line 691
  143101:  1C 8F 00 00 00     JMP          loc_143191        ; Rel: +0x8F
loc_143106:
  143106:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  14310B:  01 03 00 00 00     PUSH_INT     3
  143110:  0D                 EQ           
  143111:  18 18 00 00 00     JMP_FALSE    loc_14312A        ; Rel: +0x18
  143116:  01 2A 00 00 00     PUSH_INT     42
  14311B:  26 AF 5C 00 00     ASSIGN       fillInventoryShownModels_local5
  143120:  19 B5 02 00 00     LINE_NUM     693               ; Code Line 693
  143125:  1C 6B 00 00 00     JMP          loc_143191        ; Rel: +0x6B
loc_14312A:
  14312A:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  14312F:  01 04 00 00 00     PUSH_INT     4
  143134:  0D                 EQ           
  143135:  18 18 00 00 00     JMP_FALSE    loc_14314E        ; Rel: +0x18
  14313A:  01 2B 00 00 00     PUSH_INT     43
  14313F:  26 AF 5C 00 00     ASSIGN       fillInventoryShownModels_local5
  143144:  19 B7 02 00 00     LINE_NUM     695               ; Code Line 695
  143149:  1C 47 00 00 00     JMP          loc_143191        ; Rel: +0x47
loc_14314E:
  14314E:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  143153:  01 0A 00 00 00     PUSH_INT     10
  143158:  0D                 EQ           
  143159:  18 18 00 00 00     JMP_FALSE    loc_143172        ; Rel: +0x18
  14315E:  01 50 00 00 00     PUSH_INT     80
  143163:  26 AF 5C 00 00     ASSIGN       fillInventoryShownModels_local5
  143168:  19 B9 02 00 00     LINE_NUM     697               ; Code Line 697
  14316D:  1C 23 00 00 00     JMP          loc_143191        ; Rel: +0x23
loc_143172:
  143172:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  143177:  01 0B 00 00 00     PUSH_INT     11
  14317C:  0D                 EQ           
  14317D:  18 13 00 00 00     JMP_FALSE    loc_143191        ; Rel: +0x13
  143182:  01 51 00 00 00     PUSH_INT     81
  143187:  26 AF 5C 00 00     ASSIGN       fillInventoryShownModels_local5
  14318C:  19 BB 02 00 00     LINE_NUM     699               ; Code Line 699
loc_143191:
  143191:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  143196:  01 00 00 00 00     PUSH_INT     0
  14319B:  0D                 EQ           
  14319C:  2D 10 00 00 00     OR_JMP       loc_1431AD        ; Rel: +0x10
  1431A1:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1431A6:  01 05 00 00 00     PUSH_INT     5
  1431AB:  0D                 EQ           
  1431AC:  0E                 LOG_OR       
loc_1431AD:
  1431AD:  2D 10 00 00 00     OR_JMP       loc_1431BE        ; Rel: +0x10
  1431B2:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1431B7:  01 08 00 00 00     PUSH_INT     8
  1431BC:  0D                 EQ           
  1431BD:  0E                 LOG_OR       
loc_1431BE:
  1431BE:  2D 10 00 00 00     OR_JMP       loc_1431CF        ; Rel: +0x10
  1431C3:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1431C8:  01 06 00 00 00     PUSH_INT     6
  1431CD:  0D                 EQ           
  1431CE:  0E                 LOG_OR       
loc_1431CF:
  1431CF:  18 F8 01 00 00     JMP_FALSE    loc_1433C8        ; Rel: +0x1F8
  1431D4:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  1431D9:  26 93 10 00 00     ASSIGN       modelCount_arg0
  1431DE:  1A                 ARG_COMMIT   
  1431DF:  1E A8 03 00 00     CALL_FUNC    modelCount
  1431E4:  26 B0 5C 00 00     ASSIGN       fillInventoryShownModels_local6
  1431E9:  19 C4 02 00 00     LINE_NUM     708               ; Code Line 708
  1431EE:  19 C5 02 00 00     LINE_NUM     709               ; Code Line 709
  1431F3:  19 C6 02 00 00     LINE_NUM     710               ; Code Line 710
  1431F8:  01 00 00 00 00     PUSH_INT     0
  1431FD:  26 B1 5C 00 00     ASSIGN       fillInventoryShownModels_local7
  143202:  19 C7 02 00 00     LINE_NUM     711               ; Code Line 711
loc_143207:
  143207:  24 B1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local7
  14320C:  24 B0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local6
  143211:  10                 LT           
  143212:  18 E3 00 00 00     JMP_FALSE    loc_1432F6        ; Rel: +0xE3
  143217:  1C 13 00 00 00     JMP          loc_14322B        ; Rel: +0x13
loc_14321C:
  14321C:  22 B1 5C 00 00     PRE_INC      fillInventoryShownModels_local7
  143221:  19 C7 02 00 00     LINE_NUM     711               ; Code Line 711
  143226:  1C E0 FF FF FF     JMP          loc_143207        ; Rel: 0x-20
loc_14322B:
  14322B:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  143230:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143235:  1A                 ARG_COMMIT   
  143236:  24 B1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local7
  14323B:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143240:  1A                 ARG_COMMIT   
  143241:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  143246:  26 B2 5C 00 00     ASSIGN       fillInventoryShownModels_local8
  14324B:  19 C9 02 00 00     LINE_NUM     713               ; Code Line 713
  143250:  19 CA 02 00 00     LINE_NUM     714               ; Code Line 714
  143255:  24 B2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local8
  14325A:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  14325F:  1A                 ARG_COMMIT   
  143260:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  143265:  05                 LOG_NOT      
  143266:  2C 1B 00 00 00     AND_JMP      loc_143282        ; Rel: +0x1B
  14326B:  24 B2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local8
  143270:  26 45 11 00 00     ASSIGN       modelLight_arg0
  143275:  1A                 ARG_COMMIT   
  143276:  1E 19 04 00 00     CALL_FUNC    modelLight
  14327B:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  143280:  0F                 GT           
  143281:  15                 LOG_AND      
loc_143282:
  143282:  18 6E 00 00 00     JMP_FALSE    loc_1432F1        ; Rel: +0x6E
  143287:  24 B2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local8
  14328C:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  143291:  1A                 ARG_COMMIT   
  143292:  1E F3 03 00 00     CALL_FUNC    modelCategory
  143297:  26 B3 5C 00 00     ASSIGN       fillInventoryShownModels_local9
  14329C:  19 CD 02 00 00     LINE_NUM     717               ; Code Line 717
  1432A1:  19 CE 02 00 00     LINE_NUM     718               ; Code Line 718
  1432A6:  24 AC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local2
  1432AB:  2D 21 00 00 00     OR_JMP       loc_1432CD        ; Rel: +0x21
  1432B0:  24 B3 5C 00 00     PUSH_VAR     fillInventoryShownModels_local9
  1432B5:  01 4A 00 00 00     PUSH_INT     74
  1432BA:  14                 NE           
  1432BB:  2C 10 00 00 00     AND_JMP      loc_1432CC        ; Rel: +0x10
  1432C0:  24 B3 5C 00 00     PUSH_VAR     fillInventoryShownModels_local9
  1432C5:  01 4C 00 00 00     PUSH_INT     76
  1432CA:  14                 NE           
  1432CB:  15                 LOG_AND      
loc_1432CC:
  1432CC:  0E                 LOG_OR       
loc_1432CD:
  1432CD:  18 23 00 00 00     JMP_FALSE    loc_1432F1        ; Rel: +0x23
  1432D2:  24 B2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local8
  1432D7:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  1432DC:  28                 ARRAY_IDX    
  1432DD:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  1432E2:  19 D1 02 00 00     LINE_NUM     721               ; Code Line 721
  1432E7:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  1432EC:  19 D2 02 00 00     LINE_NUM     722               ; Code Line 722
loc_1432F1:
  1432F1:  1C 2A FF FF FF     JMP          loc_14321C        ; Rel: 0x-D6
loc_1432F6:
  1432F6:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  1432FB:  26 93 10 00 00     ASSIGN       modelCount_arg0
  143300:  1A                 ARG_COMMIT   
  143301:  1E A8 03 00 00     CALL_FUNC    modelCount
  143306:  26 B0 5C 00 00     ASSIGN       fillInventoryShownModels_local6
  14330B:  19 D9 02 00 00     LINE_NUM     729               ; Code Line 729
  143310:  01 00 00 00 00     PUSH_INT     0
  143315:  26 B1 5C 00 00     ASSIGN       fillInventoryShownModels_local7
  14331A:  19 DA 02 00 00     LINE_NUM     730               ; Code Line 730
loc_14331F:
  14331F:  24 B1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local7
  143324:  24 B0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local6
  143329:  10                 LT           
  14332A:  18 98 00 00 00     JMP_FALSE    loc_1433C3        ; Rel: +0x98
  14332F:  1C 13 00 00 00     JMP          loc_143343        ; Rel: +0x13
loc_143334:
  143334:  22 B1 5C 00 00     PRE_INC      fillInventoryShownModels_local7
  143339:  19 DA 02 00 00     LINE_NUM     730               ; Code Line 730
  14333E:  1C E0 FF FF FF     JMP          loc_14331F        ; Rel: 0x-20
loc_143343:
  143343:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143348:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  14334D:  1A                 ARG_COMMIT   
  14334E:  24 B1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local7
  143353:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143358:  1A                 ARG_COMMIT   
  143359:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  14335E:  26 B4 5C 00 00     ASSIGN       fillInventoryShownModels_local10
  143363:  19 DC 02 00 00     LINE_NUM     732               ; Code Line 732
  143368:  19 DD 02 00 00     LINE_NUM     733               ; Code Line 733
  14336D:  24 B4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local10
  143372:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  143377:  1A                 ARG_COMMIT   
  143378:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  14337D:  05                 LOG_NOT      
  14337E:  2C 1B 00 00 00     AND_JMP      loc_14339A        ; Rel: +0x1B
  143383:  24 B4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local10
  143388:  26 45 11 00 00     ASSIGN       modelLight_arg0
  14338D:  1A                 ARG_COMMIT   
  14338E:  1E 19 04 00 00     CALL_FUNC    modelLight
  143393:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  143398:  0F                 GT           
  143399:  15                 LOG_AND      
loc_14339A:
  14339A:  18 23 00 00 00     JMP_FALSE    loc_1433BE        ; Rel: +0x23
  14339F:  24 B4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local10
  1433A4:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  1433A9:  28                 ARRAY_IDX    
  1433AA:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  1433AF:  19 E1 02 00 00     LINE_NUM     737               ; Code Line 737
  1433B4:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  1433B9:  19 E2 02 00 00     LINE_NUM     738               ; Code Line 738
loc_1433BE:
  1433BE:  1C 75 FF FF FF     JMP          loc_143334        ; Rel: 0x-8B
loc_1433C3:
  1433C3:  1C 9A 11 00 00     JMP          loc_14455E        ; Rel: +0x119A
loc_1433C8:
  1433C8:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1433CD:  01 09 00 00 00     PUSH_INT     9
  1433D2:  0D                 EQ           
  1433D3:  18 15 01 00 00     JMP_FALSE    loc_1434E9        ; Rel: +0x115
  1433D8:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  1433DD:  26 93 10 00 00     ASSIGN       modelCount_arg0
  1433E2:  1A                 ARG_COMMIT   
  1433E3:  1E A8 03 00 00     CALL_FUNC    modelCount
  1433E8:  26 B5 5C 00 00     ASSIGN       fillInventoryShownModels_local11
  1433ED:  19 E9 02 00 00     LINE_NUM     745               ; Code Line 745
  1433F2:  19 EA 02 00 00     LINE_NUM     746               ; Code Line 746
  1433F7:  19 EB 02 00 00     LINE_NUM     747               ; Code Line 747
  1433FC:  01 00 00 00 00     PUSH_INT     0
  143401:  26 B6 5C 00 00     ASSIGN       fillInventoryShownModels_local12
  143406:  19 EC 02 00 00     LINE_NUM     748               ; Code Line 748
loc_14340B:
  14340B:  24 B6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local12
  143410:  24 B5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local11
  143415:  10                 LT           
  143416:  18 CD 00 00 00     JMP_FALSE    loc_1434E4        ; Rel: +0xCD
  14341B:  1C 13 00 00 00     JMP          loc_14342F        ; Rel: +0x13
loc_143420:
  143420:  22 B6 5C 00 00     PRE_INC      fillInventoryShownModels_local12
  143425:  19 EC 02 00 00     LINE_NUM     748               ; Code Line 748
  14342A:  1C E0 FF FF FF     JMP          loc_14340B        ; Rel: 0x-20
loc_14342F:
  14342F:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  143434:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143439:  1A                 ARG_COMMIT   
  14343A:  24 B6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local12
  14343F:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143444:  1A                 ARG_COMMIT   
  143445:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  14344A:  26 B7 5C 00 00     ASSIGN       fillInventoryShownModels_local13
  14344F:  19 EE 02 00 00     LINE_NUM     750               ; Code Line 750
  143454:  19 EF 02 00 00     LINE_NUM     751               ; Code Line 751
  143459:  24 B7 5C 00 00     PUSH_VAR     fillInventoryShownModels_local13
  14345E:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  143463:  1A                 ARG_COMMIT   
  143464:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  143469:  05                 LOG_NOT      
  14346A:  18 74 00 00 00     JMP_FALSE    loc_1434DF        ; Rel: +0x74
  14346F:  24 B7 5C 00 00     PUSH_VAR     fillInventoryShownModels_local13
  143474:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  143479:  1A                 ARG_COMMIT   
  14347A:  1E F3 03 00 00     CALL_FUNC    modelCategory
  14347F:  26 B8 5C 00 00     ASSIGN       fillInventoryShownModels_local14
  143484:  19 F3 02 00 00     LINE_NUM     755               ; Code Line 755
  143489:  19 F4 02 00 00     LINE_NUM     756               ; Code Line 756
  14348E:  24 B8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local14
  143493:  01 4A 00 00 00     PUSH_INT     74
  143498:  14                 NE           
  143499:  2C 10 00 00 00     AND_JMP      loc_1434AA        ; Rel: +0x10
  14349E:  24 B8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local14
  1434A3:  01 4C 00 00 00     PUSH_INT     76
  1434A8:  14                 NE           
  1434A9:  15                 LOG_AND      
loc_1434AA:
  1434AA:  2C 10 00 00 00     AND_JMP      loc_1434BB        ; Rel: +0x10
  1434AF:  24 B8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local14
  1434B4:  01 50 00 00 00     PUSH_INT     80
  1434B9:  14                 NE           
  1434BA:  15                 LOG_AND      
loc_1434BB:
  1434BB:  18 23 00 00 00     JMP_FALSE    loc_1434DF        ; Rel: +0x23
  1434C0:  24 B7 5C 00 00     PUSH_VAR     fillInventoryShownModels_local13
  1434C5:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  1434CA:  28                 ARRAY_IDX    
  1434CB:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  1434D0:  19 F7 02 00 00     LINE_NUM     759               ; Code Line 759
  1434D5:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  1434DA:  19 F8 02 00 00     LINE_NUM     760               ; Code Line 760
loc_1434DF:
  1434DF:  1C 40 FF FF FF     JMP          loc_143420        ; Rel: 0x-C0
loc_1434E4:
  1434E4:  1C 79 10 00 00     JMP          loc_14455E        ; Rel: +0x1079
loc_1434E9:
  1434E9:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1434EE:  01 02 00 00 00     PUSH_INT     2
  1434F3:  0D                 EQ           
  1434F4:  18 AC 03 00 00     JMP_FALSE    loc_1438A1        ; Rel: +0x3AC
  1434F9:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  1434FE:  26 93 10 00 00     ASSIGN       modelCount_arg0
  143503:  1A                 ARG_COMMIT   
  143504:  1E A8 03 00 00     CALL_FUNC    modelCount
  143509:  26 B9 5C 00 00     ASSIGN       fillInventoryShownModels_local15
  14350E:  19 01 03 00 00     LINE_NUM     769               ; Code Line 769
  143513:  19 02 03 00 00     LINE_NUM     770               ; Code Line 770
  143518:  19 03 03 00 00     LINE_NUM     771               ; Code Line 771
  14351D:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  143522:  18 0D 01 00 00     JMP_FALSE    loc_143630        ; Rel: +0x10D
  143527:  01 00 00 00 00     PUSH_INT     0
  14352C:  26 BA 5C 00 00     ASSIGN       fillInventoryShownModels_local16
  143531:  19 06 03 00 00     LINE_NUM     774               ; Code Line 774
loc_143536:
  143536:  24 BA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local16
  14353B:  24 B9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local15
  143540:  10                 LT           
  143541:  18 EE 00 00 00     JMP_FALSE    loc_143630        ; Rel: +0xEE
  143546:  1C 13 00 00 00     JMP          loc_14355A        ; Rel: +0x13
loc_14354B:
  14354B:  22 BA 5C 00 00     PRE_INC      fillInventoryShownModels_local16
  143550:  19 06 03 00 00     LINE_NUM     774               ; Code Line 774
  143555:  1C E0 FF FF FF     JMP          loc_143536        ; Rel: 0x-20
loc_14355A:
  14355A:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  14355F:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143564:  1A                 ARG_COMMIT   
  143565:  24 BA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local16
  14356A:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  14356F:  1A                 ARG_COMMIT   
  143570:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  143575:  26 BB 5C 00 00     ASSIGN       fillInventoryShownModels_local17
  14357A:  19 08 03 00 00     LINE_NUM     776               ; Code Line 776
  14357F:  19 09 03 00 00     LINE_NUM     777               ; Code Line 777
  143584:  24 BB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local17
  143589:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  14358E:  1A                 ARG_COMMIT   
  14358F:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  143594:  05                 LOG_NOT      
  143595:  18 95 00 00 00     JMP_FALSE    loc_14362B        ; Rel: +0x95
  14359A:  24 BB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local17
  14359F:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  1435A4:  1A                 ARG_COMMIT   
  1435A5:  1E F3 03 00 00     CALL_FUNC    modelCategory
  1435AA:  26 BC 5C 00 00     ASSIGN       fillInventoryShownModels_local18
  1435AF:  19 0D 03 00 00     LINE_NUM     781               ; Code Line 781
  1435B4:  19 0E 03 00 00     LINE_NUM     782               ; Code Line 782
  1435B9:  24 BC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local18
  1435BE:  01 28 00 00 00     PUSH_INT     40
  1435C3:  0D                 EQ           
  1435C4:  2D 10 00 00 00     OR_JMP       loc_1435D5        ; Rel: +0x10
  1435C9:  24 BC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local18
  1435CE:  01 2F 00 00 00     PUSH_INT     47
  1435D3:  0D                 EQ           
  1435D4:  0E                 LOG_OR       
loc_1435D5:
  1435D5:  2D 10 00 00 00     OR_JMP       loc_1435E6        ; Rel: +0x10
  1435DA:  24 BC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local18
  1435DF:  01 29 00 00 00     PUSH_INT     41
  1435E4:  0D                 EQ           
  1435E5:  0E                 LOG_OR       
loc_1435E6:
  1435E6:  18 44 00 00 00     JMP_FALSE    loc_14362B        ; Rel: +0x44
  1435EB:  24 30 5C 00 00     PUSH_VAR     armorCategoryFilter
  1435F0:  01 00 00 00 00     PUSH_INT     0
  1435F5:  0D                 EQ           
  1435F6:  2D 10 00 00 00     OR_JMP       loc_143607        ; Rel: +0x10
  1435FB:  24 BC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local18
  143600:  24 30 5C 00 00     PUSH_VAR     armorCategoryFilter
  143605:  0D                 EQ           
  143606:  0E                 LOG_OR       
loc_143607:
  143607:  18 23 00 00 00     JMP_FALSE    loc_14362B        ; Rel: +0x23
  14360C:  24 BB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local17
  143611:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  143616:  28                 ARRAY_IDX    
  143617:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  14361C:  19 13 03 00 00     LINE_NUM     787               ; Code Line 787
  143621:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  143626:  19 14 03 00 00     LINE_NUM     788               ; Code Line 788
loc_14362B:
  14362B:  1C 1F FF FF FF     JMP          loc_14354B        ; Rel: 0x-E1
loc_143630:
  143630:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143635:  26 93 10 00 00     ASSIGN       modelCount_arg0
  14363A:  1A                 ARG_COMMIT   
  14363B:  1E A8 03 00 00     CALL_FUNC    modelCount
  143640:  26 B9 5C 00 00     ASSIGN       fillInventoryShownModels_local15
  143645:  19 1D 03 00 00     LINE_NUM     797               ; Code Line 797
  14364A:  01 00 00 00 00     PUSH_INT     0
  14364F:  26 BA 5C 00 00     ASSIGN       fillInventoryShownModels_local16
  143654:  19 1E 03 00 00     LINE_NUM     798               ; Code Line 798
loc_143659:
  143659:  24 BA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local16
  14365E:  24 B9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local15
  143663:  10                 LT           
  143664:  18 37 02 00 00     JMP_FALSE    loc_14389C        ; Rel: +0x237
  143669:  1C 13 00 00 00     JMP          loc_14367D        ; Rel: +0x13
loc_14366E:
  14366E:  22 BA 5C 00 00     PRE_INC      fillInventoryShownModels_local16
  143673:  19 1E 03 00 00     LINE_NUM     798               ; Code Line 798
  143678:  1C E0 FF FF FF     JMP          loc_143659        ; Rel: 0x-20
loc_14367D:
  14367D:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143682:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143687:  1A                 ARG_COMMIT   
  143688:  24 BA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local16
  14368D:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143692:  1A                 ARG_COMMIT   
  143693:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  143698:  26 BD 5C 00 00     ASSIGN       fillInventoryShownModels_local19
  14369D:  19 20 03 00 00     LINE_NUM     800               ; Code Line 800
  1436A2:  19 21 03 00 00     LINE_NUM     801               ; Code Line 801
  1436A7:  24 BD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local19
  1436AC:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  1436B1:  1A                 ARG_COMMIT   
  1436B2:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  1436B7:  05                 LOG_NOT      
  1436B8:  2C 1B 00 00 00     AND_JMP      loc_1436D4        ; Rel: +0x1B
  1436BD:  24 BD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local19
  1436C2:  26 45 11 00 00     ASSIGN       modelLight_arg0
  1436C7:  1A                 ARG_COMMIT   
  1436C8:  1E 19 04 00 00     CALL_FUNC    modelLight
  1436CD:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  1436D2:  0F                 GT           
  1436D3:  15                 LOG_AND      
loc_1436D4:
  1436D4:  18 C2 01 00 00     JMP_FALSE    loc_143897        ; Rel: +0x1C2
  1436D9:  24 BD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local19
  1436DE:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  1436E3:  1A                 ARG_COMMIT   
  1436E4:  1E F3 03 00 00     CALL_FUNC    modelCategory
  1436E9:  26 BE 5C 00 00     ASSIGN       fillInventoryShownModels_local20
  1436EE:  19 25 03 00 00     LINE_NUM     805               ; Code Line 805
  1436F3:  19 26 03 00 00     LINE_NUM     806               ; Code Line 806
  1436F8:  24 BE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local20
  1436FD:  01 28 00 00 00     PUSH_INT     40
  143702:  0D                 EQ           
  143703:  2D 10 00 00 00     OR_JMP       loc_143714        ; Rel: +0x10
  143708:  24 BE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local20
  14370D:  01 2F 00 00 00     PUSH_INT     47
  143712:  0D                 EQ           
  143713:  0E                 LOG_OR       
loc_143714:
  143714:  2D 10 00 00 00     OR_JMP       loc_143725        ; Rel: +0x10
  143719:  24 BE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local20
  14371E:  01 29 00 00 00     PUSH_INT     41
  143723:  0D                 EQ           
  143724:  0E                 LOG_OR       
loc_143725:
  143725:  18 71 01 00 00     JMP_FALSE    loc_143897        ; Rel: +0x171
  14372A:  24 30 5C 00 00     PUSH_VAR     armorCategoryFilter
  14372F:  01 00 00 00 00     PUSH_INT     0
  143734:  0D                 EQ           
  143735:  2D 10 00 00 00     OR_JMP       loc_143746        ; Rel: +0x10
  14373A:  24 BE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local20
  14373F:  24 30 5C 00 00     PUSH_VAR     armorCategoryFilter
  143744:  0D                 EQ           
  143745:  0E                 LOG_OR       
loc_143746:
  143746:  18 50 01 00 00     JMP_FALSE    loc_143897        ; Rel: +0x150
  14374B:  01 01 00 00 00     PUSH_INT     1
  143750:  26 BF 5C 00 00     ASSIGN       fillInventoryShownModels_local21
  143755:  19 2A 03 00 00     LINE_NUM     810               ; Code Line 810
  14375A:  19 2B 03 00 00     LINE_NUM     811               ; Code Line 811
  14375F:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  143764:  05                 LOG_NOT      
  143765:  18 08 01 00 00     JMP_FALSE    loc_14386E        ; Rel: +0x108
  14376A:  24 BD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local19
  14376F:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  143774:  1A                 ARG_COMMIT   
  143775:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  14377A:  26 C0 5C 00 00     ASSIGN       fillInventoryShownModels_local22
  14377F:  19 2E 03 00 00     LINE_NUM     814               ; Code Line 814
  143784:  19 2F 03 00 00     LINE_NUM     815               ; Code Line 815
  143789:  01 EE 00 00 00     PUSH_INT     238
  14378E:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143793:  1A                 ARG_COMMIT   
  143794:  24 BE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local20
  143799:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  14379E:  1A                 ARG_COMMIT   
  14379F:  24 C0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local22
  1437A4:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  1437A9:  1A                 ARG_COMMIT   
  1437AA:  01 C1 BD F0 FF     PUSH_INT     -999999
  1437AF:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  1437B4:  1A                 ARG_COMMIT   
  1437B5:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  1437BA:  26 C1 5C 00 00     ASSIGN       fillInventoryShownModels_local23
  1437BF:  19 2F 03 00 00     LINE_NUM     815               ; Code Line 815
  1437C4:  19 30 03 00 00     LINE_NUM     816               ; Code Line 816
  1437C9:  01 44 01 00 00     PUSH_INT     324
  1437CE:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  1437D3:  1A                 ARG_COMMIT   
  1437D4:  24 BE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local20
  1437D9:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  1437DE:  1A                 ARG_COMMIT   
  1437DF:  24 C0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local22
  1437E4:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  1437E9:  1A                 ARG_COMMIT   
  1437EA:  01 C1 BD F0 FF     PUSH_INT     -999999
  1437EF:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  1437F4:  1A                 ARG_COMMIT   
  1437F5:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  1437FA:  26 C2 5C 00 00     ASSIGN       fillInventoryShownModels_local24
  1437FF:  19 30 03 00 00     LINE_NUM     816               ; Code Line 816
  143804:  19 31 03 00 00     LINE_NUM     817               ; Code Line 817
  143809:  24 C1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local23
  14380E:  01 00 00 00 00     PUSH_INT     0
  143813:  0F                 GT           
  143814:  2C 10 00 00 00     AND_JMP      loc_143825        ; Rel: +0x10
  143819:  24 C1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local23
  14381E:  01 1E 00 00 00     PUSH_INT     30
  143823:  10                 LT           
  143824:  15                 LOG_AND      
loc_143825:
  143825:  2C 10 00 00 00     AND_JMP      loc_143836        ; Rel: +0x10
  14382A:  24 C2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local24
  14382F:  01 0B 00 00 00     PUSH_INT     11
  143834:  14                 NE           
  143835:  15                 LOG_AND      
loc_143836:
  143836:  26 BF 5C 00 00     ASSIGN       fillInventoryShownModels_local21
  14383B:  19 32 03 00 00     LINE_NUM     818               ; Code Line 818
  143840:  24 BF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local21
  143845:  18 28 00 00 00     JMP_FALSE    loc_14386E        ; Rel: +0x28
  14384A:  24 BD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local19
  14384F:  26 1A 2A 00 00     ASSIGN       isModelInAnySet_arg0
  143854:  1A                 ARG_COMMIT   
  143855:  1E C5 08 00 00     CALL_FUNC    isModelInAnySet
  14385A:  18 13 00 00 00     JMP_FALSE    loc_14386E        ; Rel: +0x13
  14385F:  01 00 00 00 00     PUSH_INT     0
  143864:  26 BF 5C 00 00     ASSIGN       fillInventoryShownModels_local21
  143869:  19 36 03 00 00     LINE_NUM     822               ; Code Line 822
loc_14386E:
  14386E:  24 BF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local21
  143873:  18 23 00 00 00     JMP_FALSE    loc_143897        ; Rel: +0x23
  143878:  24 BD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local19
  14387D:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  143882:  28                 ARRAY_IDX    
  143883:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  143888:  19 3B 03 00 00     LINE_NUM     827               ; Code Line 827
  14388D:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  143892:  19 3C 03 00 00     LINE_NUM     828               ; Code Line 828
loc_143897:
  143897:  1C D6 FD FF FF     JMP          loc_14366E        ; Rel: 0x-22A
loc_14389C:
  14389C:  1C C1 0C 00 00     JMP          loc_14455E        ; Rel: +0xCC1
loc_1438A1:
  1438A1:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  1438A6:  01 01 00 00 00     PUSH_INT     1
  1438AB:  0D                 EQ           
  1438AC:  18 79 04 00 00     JMP_FALSE    loc_143D26        ; Rel: +0x479
  1438B1:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  1438B6:  26 93 10 00 00     ASSIGN       modelCount_arg0
  1438BB:  1A                 ARG_COMMIT   
  1438BC:  1E A8 03 00 00     CALL_FUNC    modelCount
  1438C1:  26 C3 5C 00 00     ASSIGN       fillInventoryShownModels_local25
  1438C6:  19 47 03 00 00     LINE_NUM     839               ; Code Line 839
  1438CB:  19 48 03 00 00     LINE_NUM     840               ; Code Line 840
  1438D0:  19 49 03 00 00     LINE_NUM     841               ; Code Line 841
  1438D5:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  1438DA:  18 83 01 00 00     JMP_FALSE    loc_143A5E        ; Rel: +0x183
  1438DF:  01 00 00 00 00     PUSH_INT     0
  1438E4:  26 C4 5C 00 00     ASSIGN       fillInventoryShownModels_local26
  1438E9:  19 4C 03 00 00     LINE_NUM     844               ; Code Line 844
loc_1438EE:
  1438EE:  24 C4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local26
  1438F3:  24 C3 5C 00 00     PUSH_VAR     fillInventoryShownModels_local25
  1438F8:  10                 LT           
  1438F9:  18 64 01 00 00     JMP_FALSE    loc_143A5E        ; Rel: +0x164
  1438FE:  1C 13 00 00 00     JMP          loc_143912        ; Rel: +0x13
loc_143903:
  143903:  22 C4 5C 00 00     PRE_INC      fillInventoryShownModels_local26
  143908:  19 4C 03 00 00     LINE_NUM     844               ; Code Line 844
  14390D:  1C E0 FF FF FF     JMP          loc_1438EE        ; Rel: 0x-20
loc_143912:
  143912:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  143917:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  14391C:  1A                 ARG_COMMIT   
  14391D:  24 C4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local26
  143922:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143927:  1A                 ARG_COMMIT   
  143928:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  14392D:  26 C5 5C 00 00     ASSIGN       fillInventoryShownModels_local27
  143932:  19 4E 03 00 00     LINE_NUM     846               ; Code Line 846
  143937:  19 4F 03 00 00     LINE_NUM     847               ; Code Line 847
  14393C:  24 C5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local27
  143941:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  143946:  1A                 ARG_COMMIT   
  143947:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  14394C:  05                 LOG_NOT      
  14394D:  18 0B 01 00 00     JMP_FALSE    loc_143A59        ; Rel: +0x10B
  143952:  24 C5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local27
  143957:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  14395C:  1A                 ARG_COMMIT   
  14395D:  1E F3 03 00 00     CALL_FUNC    modelCategory
  143962:  26 C6 5C 00 00     ASSIGN       fillInventoryShownModels_local28
  143967:  19 53 03 00 00     LINE_NUM     851               ; Code Line 851
  14396C:  19 54 03 00 00     LINE_NUM     852               ; Code Line 852
  143971:  24 C6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local28
  143976:  01 27 00 00 00     PUSH_INT     39
  14397B:  0D                 EQ           
  14397C:  18 DC 00 00 00     JMP_FALSE    loc_143A59        ; Rel: +0xDC
  143981:  24 C5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local27
  143986:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  14398B:  1A                 ARG_COMMIT   
  14398C:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  143991:  26 C7 5C 00 00     ASSIGN       fillInventoryShownModels_local29
  143996:  19 57 03 00 00     LINE_NUM     855               ; Code Line 855
  14399B:  19 58 03 00 00     LINE_NUM     856               ; Code Line 856
  1439A0:  24 2F 5C 00 00     PUSH_VAR     weaponTypeFilter
  1439A5:  01 00 00 00 00     PUSH_INT     0
  1439AA:  0D                 EQ           
  1439AB:  2D 3C 00 00 00     OR_JMP       loc_1439E8        ; Rel: +0x3C
  1439B0:  24 2F 5C 00 00     PUSH_VAR     weaponTypeFilter
  1439B5:  01 6D 00 00 00     PUSH_INT     109
  1439BA:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  1439BF:  1A                 ARG_COMMIT   
  1439C0:  24 C6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local28
  1439C5:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  1439CA:  1A                 ARG_COMMIT   
  1439CB:  24 C7 5C 00 00     PUSH_VAR     fillInventoryShownModels_local29
  1439D0:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  1439D5:  1A                 ARG_COMMIT   
  1439D6:  01 C1 BD F0 FF     PUSH_INT     -999999
  1439DB:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  1439E0:  1A                 ARG_COMMIT   
  1439E1:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  1439E6:  0D                 EQ           
  1439E7:  0E                 LOG_OR       
loc_1439E8:
  1439E8:  18 70 00 00 00     JMP_FALSE    loc_143A59        ; Rel: +0x70
  1439ED:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  1439F2:  01 FF FF FF FF     PUSH_INT     -1
  1439F7:  0D                 EQ           
  1439F8:  2D 3C 00 00 00     OR_JMP       loc_143A35        ; Rel: +0x3C
  1439FD:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  143A02:  01 1E 02 00 00     PUSH_INT     542
  143A07:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143A0C:  1A                 ARG_COMMIT   
  143A0D:  24 C6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local28
  143A12:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  143A17:  1A                 ARG_COMMIT   
  143A18:  24 C7 5C 00 00     PUSH_VAR     fillInventoryShownModels_local29
  143A1D:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  143A22:  1A                 ARG_COMMIT   
  143A23:  01 C1 BD F0 FF     PUSH_INT     -999999
  143A28:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  143A2D:  1A                 ARG_COMMIT   
  143A2E:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  143A33:  0D                 EQ           
  143A34:  0E                 LOG_OR       
loc_143A35:
  143A35:  18 23 00 00 00     JMP_FALSE    loc_143A59        ; Rel: +0x23
  143A3A:  24 C5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local27
  143A3F:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  143A44:  28                 ARRAY_IDX    
  143A45:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  143A4A:  19 5D 03 00 00     LINE_NUM     861               ; Code Line 861
  143A4F:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  143A54:  19 5E 03 00 00     LINE_NUM     862               ; Code Line 862
loc_143A59:
  143A59:  1C A9 FE FF FF     JMP          loc_143903        ; Rel: 0x-157
loc_143A5E:
  143A5E:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143A63:  26 93 10 00 00     ASSIGN       modelCount_arg0
  143A68:  1A                 ARG_COMMIT   
  143A69:  1E A8 03 00 00     CALL_FUNC    modelCount
  143A6E:  26 C3 5C 00 00     ASSIGN       fillInventoryShownModels_local25
  143A73:  19 68 03 00 00     LINE_NUM     872               ; Code Line 872
  143A78:  01 00 00 00 00     PUSH_INT     0
  143A7D:  26 C4 5C 00 00     ASSIGN       fillInventoryShownModels_local26
  143A82:  19 69 03 00 00     LINE_NUM     873               ; Code Line 873
loc_143A87:
  143A87:  24 C4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local26
  143A8C:  24 C3 5C 00 00     PUSH_VAR     fillInventoryShownModels_local25
  143A91:  10                 LT           
  143A92:  18 8E 02 00 00     JMP_FALSE    loc_143D21        ; Rel: +0x28E
  143A97:  1C 13 00 00 00     JMP          loc_143AAB        ; Rel: +0x13
loc_143A9C:
  143A9C:  22 C4 5C 00 00     PRE_INC      fillInventoryShownModels_local26
  143AA1:  19 69 03 00 00     LINE_NUM     873               ; Code Line 873
  143AA6:  1C E0 FF FF FF     JMP          loc_143A87        ; Rel: 0x-20
loc_143AAB:
  143AAB:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143AB0:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143AB5:  1A                 ARG_COMMIT   
  143AB6:  24 C4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local26
  143ABB:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143AC0:  1A                 ARG_COMMIT   
  143AC1:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  143AC6:  26 C8 5C 00 00     ASSIGN       fillInventoryShownModels_local30
  143ACB:  19 6B 03 00 00     LINE_NUM     875               ; Code Line 875
  143AD0:  19 6C 03 00 00     LINE_NUM     876               ; Code Line 876
  143AD5:  24 C8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local30
  143ADA:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  143ADF:  1A                 ARG_COMMIT   
  143AE0:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  143AE5:  05                 LOG_NOT      
  143AE6:  2C 1B 00 00 00     AND_JMP      loc_143B02        ; Rel: +0x1B
  143AEB:  24 C8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local30
  143AF0:  26 45 11 00 00     ASSIGN       modelLight_arg0
  143AF5:  1A                 ARG_COMMIT   
  143AF6:  1E 19 04 00 00     CALL_FUNC    modelLight
  143AFB:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  143B00:  0F                 GT           
  143B01:  15                 LOG_AND      
loc_143B02:
  143B02:  18 19 02 00 00     JMP_FALSE    loc_143D1C        ; Rel: +0x219
  143B07:  24 C8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local30
  143B0C:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  143B11:  1A                 ARG_COMMIT   
  143B12:  1E F3 03 00 00     CALL_FUNC    modelCategory
  143B17:  26 C9 5C 00 00     ASSIGN       fillInventoryShownModels_local31
  143B1C:  19 70 03 00 00     LINE_NUM     880               ; Code Line 880
  143B21:  19 71 03 00 00     LINE_NUM     881               ; Code Line 881
  143B26:  24 C9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local31
  143B2B:  01 27 00 00 00     PUSH_INT     39
  143B30:  0D                 EQ           
  143B31:  18 EA 01 00 00     JMP_FALSE    loc_143D1C        ; Rel: +0x1EA
  143B36:  24 C8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local30
  143B3B:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  143B40:  1A                 ARG_COMMIT   
  143B41:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  143B46:  26 CA 5C 00 00     ASSIGN       fillInventoryShownModels_local32
  143B4B:  19 74 03 00 00     LINE_NUM     884               ; Code Line 884
  143B50:  19 75 03 00 00     LINE_NUM     885               ; Code Line 885
  143B55:  24 2F 5C 00 00     PUSH_VAR     weaponTypeFilter
  143B5A:  01 00 00 00 00     PUSH_INT     0
  143B5F:  0D                 EQ           
  143B60:  2D 3C 00 00 00     OR_JMP       loc_143B9D        ; Rel: +0x3C
  143B65:  24 2F 5C 00 00     PUSH_VAR     weaponTypeFilter
  143B6A:  01 6D 00 00 00     PUSH_INT     109
  143B6F:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143B74:  1A                 ARG_COMMIT   
  143B75:  24 C9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local31
  143B7A:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  143B7F:  1A                 ARG_COMMIT   
  143B80:  24 CA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local32
  143B85:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  143B8A:  1A                 ARG_COMMIT   
  143B8B:  01 C1 BD F0 FF     PUSH_INT     -999999
  143B90:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  143B95:  1A                 ARG_COMMIT   
  143B96:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  143B9B:  0D                 EQ           
  143B9C:  0E                 LOG_OR       
loc_143B9D:
  143B9D:  18 7E 01 00 00     JMP_FALSE    loc_143D1C        ; Rel: +0x17E
  143BA2:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  143BA7:  01 FF FF FF FF     PUSH_INT     -1
  143BAC:  0D                 EQ           
  143BAD:  2D 3C 00 00 00     OR_JMP       loc_143BEA        ; Rel: +0x3C
  143BB2:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  143BB7:  01 1E 02 00 00     PUSH_INT     542
  143BBC:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143BC1:  1A                 ARG_COMMIT   
  143BC2:  24 C9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local31
  143BC7:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  143BCC:  1A                 ARG_COMMIT   
  143BCD:  24 CA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local32
  143BD2:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  143BD7:  1A                 ARG_COMMIT   
  143BD8:  01 C1 BD F0 FF     PUSH_INT     -999999
  143BDD:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  143BE2:  1A                 ARG_COMMIT   
  143BE3:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  143BE8:  0D                 EQ           
  143BE9:  0E                 LOG_OR       
loc_143BEA:
  143BEA:  18 31 01 00 00     JMP_FALSE    loc_143D1C        ; Rel: +0x131
  143BEF:  01 01 00 00 00     PUSH_INT     1
  143BF4:  26 CB 5C 00 00     ASSIGN       fillInventoryShownModels_local33
  143BF9:  19 79 03 00 00     LINE_NUM     889               ; Code Line 889
  143BFE:  19 7A 03 00 00     LINE_NUM     890               ; Code Line 890
  143C03:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  143C08:  05                 LOG_NOT      
  143C09:  18 E9 00 00 00     JMP_FALSE    loc_143CF3        ; Rel: +0xE9
  143C0E:  01 EE 00 00 00     PUSH_INT     238
  143C13:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143C18:  1A                 ARG_COMMIT   
  143C19:  24 C9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local31
  143C1E:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  143C23:  1A                 ARG_COMMIT   
  143C24:  24 CA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local32
  143C29:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  143C2E:  1A                 ARG_COMMIT   
  143C2F:  01 C1 BD F0 FF     PUSH_INT     -999999
  143C34:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  143C39:  1A                 ARG_COMMIT   
  143C3A:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  143C3F:  26 CC 5C 00 00     ASSIGN       fillInventoryShownModels_local34
  143C44:  19 7C 03 00 00     LINE_NUM     892               ; Code Line 892
  143C49:  19 7D 03 00 00     LINE_NUM     893               ; Code Line 893
  143C4E:  01 44 01 00 00     PUSH_INT     324
  143C53:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143C58:  1A                 ARG_COMMIT   
  143C59:  24 C9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local31
  143C5E:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  143C63:  1A                 ARG_COMMIT   
  143C64:  24 CA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local32
  143C69:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  143C6E:  1A                 ARG_COMMIT   
  143C6F:  01 C1 BD F0 FF     PUSH_INT     -999999
  143C74:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  143C79:  1A                 ARG_COMMIT   
  143C7A:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  143C7F:  26 CD 5C 00 00     ASSIGN       fillInventoryShownModels_local35
  143C84:  19 7D 03 00 00     LINE_NUM     893               ; Code Line 893
  143C89:  19 7E 03 00 00     LINE_NUM     894               ; Code Line 894
  143C8E:  24 CC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local34
  143C93:  01 00 00 00 00     PUSH_INT     0
  143C98:  0F                 GT           
  143C99:  2C 10 00 00 00     AND_JMP      loc_143CAA        ; Rel: +0x10
  143C9E:  24 CC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local34
  143CA3:  01 1E 00 00 00     PUSH_INT     30
  143CA8:  10                 LT           
  143CA9:  15                 LOG_AND      
loc_143CAA:
  143CAA:  2C 10 00 00 00     AND_JMP      loc_143CBB        ; Rel: +0x10
  143CAF:  24 CD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local35
  143CB4:  01 0B 00 00 00     PUSH_INT     11
  143CB9:  14                 NE           
  143CBA:  15                 LOG_AND      
loc_143CBB:
  143CBB:  26 CB 5C 00 00     ASSIGN       fillInventoryShownModels_local33
  143CC0:  19 7F 03 00 00     LINE_NUM     895               ; Code Line 895
  143CC5:  24 CB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local33
  143CCA:  18 28 00 00 00     JMP_FALSE    loc_143CF3        ; Rel: +0x28
  143CCF:  24 C8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local30
  143CD4:  26 1A 2A 00 00     ASSIGN       isModelInAnySet_arg0
  143CD9:  1A                 ARG_COMMIT   
  143CDA:  1E C5 08 00 00     CALL_FUNC    isModelInAnySet
  143CDF:  18 13 00 00 00     JMP_FALSE    loc_143CF3        ; Rel: +0x13
  143CE4:  01 00 00 00 00     PUSH_INT     0
  143CE9:  26 CB 5C 00 00     ASSIGN       fillInventoryShownModels_local33
  143CEE:  19 83 03 00 00     LINE_NUM     899               ; Code Line 899
loc_143CF3:
  143CF3:  24 CB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local33
  143CF8:  18 23 00 00 00     JMP_FALSE    loc_143D1C        ; Rel: +0x23
  143CFD:  24 C8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local30
  143D02:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  143D07:  28                 ARRAY_IDX    
  143D08:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  143D0D:  19 88 03 00 00     LINE_NUM     904               ; Code Line 904
  143D12:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  143D17:  19 89 03 00 00     LINE_NUM     905               ; Code Line 905
loc_143D1C:
  143D1C:  1C 7F FD FF FF     JMP          loc_143A9C        ; Rel: 0x-281
loc_143D21:
  143D21:  1C 3C 08 00 00     JMP          loc_14455E        ; Rel: +0x83C
loc_143D26:
  143D26:  24 A9 5C 00 00     PUSH_VAR     fillInventoryShownModels_arg0
  143D2B:  01 07 00 00 00     PUSH_INT     7
  143D30:  0D                 EQ           
  143D31:  18 27 04 00 00     JMP_FALSE    loc_144159        ; Rel: +0x427
  143D36:  01 00 00 00 00     PUSH_INT     0
  143D3B:  26 CE 5C 00 00     ASSIGN       fillInventoryShownModels_local36
  143D40:  19 94 03 00 00     LINE_NUM     916               ; Code Line 916
  143D45:  19 95 03 00 00     LINE_NUM     917               ; Code Line 917
  143D4A:  02 74 65 6D 70 2E  PUSH_STR     "temp.action.open.legendary.inventory"
        61 63 74 69 6F 6E
        2E 6F 70 65 6E 2E
        6C 65 67 65 6E 64
        61 72 79 2E 69 6E
        76 65 6E 74 6F 72
        79 00
  143D70:  26 FD 02 00 00     ASSIGN       isState_arg0
  143D75:  1A                 ARG_COMMIT   
  143D76:  01 01 00 00 00     PUSH_INT     1
  143D7B:  26 FE 02 00 00     ASSIGN       isState_arg1
  143D80:  1A                 ARG_COMMIT   
  143D81:  1E 78 01 00 00     CALL_FUNC    isState
  143D86:  18 49 00 00 00     JMP_FALSE    loc_143DD0        ; Rel: +0x49
  143D8B:  02 74 65 6D 70 2E  PUSH_STR     "temp.action.open.legendary.inventory"
        61 63 74 69 6F 6E
        2E 6F 70 65 6E 2E
        6C 65 67 65 6E 64
        61 72 79 2E 69 6E
        76 65 6E 74 6F 72
        79 00
  143DB1:  26 FB 02 00 00     ASSIGN       stateRemove_arg0
  143DB6:  1A                 ARG_COMMIT   
  143DB7:  1E 76 01 00 00     CALL_FUNC    stateRemove
  143DBC:  19 99 03 00 00     LINE_NUM     921               ; Code Line 921
  143DC1:  01 01 00 00 00     PUSH_INT     1
  143DC6:  26 CE 5C 00 00     ASSIGN       fillInventoryShownModels_local36
  143DCB:  19 9A 03 00 00     LINE_NUM     922               ; Code Line 922
loc_143DD0:
  143DD0:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  143DD5:  26 93 10 00 00     ASSIGN       modelCount_arg0
  143DDA:  1A                 ARG_COMMIT   
  143DDB:  1E A8 03 00 00     CALL_FUNC    modelCount
  143DE0:  26 CF 5C 00 00     ASSIGN       fillInventoryShownModels_local37
  143DE5:  19 9D 03 00 00     LINE_NUM     925               ; Code Line 925
  143DEA:  19 9E 03 00 00     LINE_NUM     926               ; Code Line 926
  143DEF:  19 9F 03 00 00     LINE_NUM     927               ; Code Line 927
  143DF4:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  143DF9:  18 9D 01 00 00     JMP_FALSE    loc_143F97        ; Rel: +0x19D
  143DFE:  01 00 00 00 00     PUSH_INT     0
  143E03:  26 D0 5C 00 00     ASSIGN       fillInventoryShownModels_local38
  143E08:  19 A2 03 00 00     LINE_NUM     930               ; Code Line 930
loc_143E0D:
  143E0D:  24 D0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local38
  143E12:  24 CF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local37
  143E17:  10                 LT           
  143E18:  18 7E 01 00 00     JMP_FALSE    loc_143F97        ; Rel: +0x17E
  143E1D:  1C 13 00 00 00     JMP          loc_143E31        ; Rel: +0x13
loc_143E22:
  143E22:  22 D0 5C 00 00     PRE_INC      fillInventoryShownModels_local38
  143E27:  19 A2 03 00 00     LINE_NUM     930               ; Code Line 930
  143E2C:  1C E0 FF FF FF     JMP          loc_143E0D        ; Rel: 0x-20
loc_143E31:
  143E31:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  143E36:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143E3B:  1A                 ARG_COMMIT   
  143E3C:  24 D0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local38
  143E41:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  143E46:  1A                 ARG_COMMIT   
  143E47:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  143E4C:  26 D1 5C 00 00     ASSIGN       fillInventoryShownModels_local39
  143E51:  19 A4 03 00 00     LINE_NUM     932               ; Code Line 932
  143E56:  19 A5 03 00 00     LINE_NUM     933               ; Code Line 933
  143E5B:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143E60:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  143E65:  1A                 ARG_COMMIT   
  143E66:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  143E6B:  05                 LOG_NOT      
  143E6C:  18 25 01 00 00     JMP_FALSE    loc_143F92        ; Rel: +0x125
  143E71:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143E76:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  143E7B:  1A                 ARG_COMMIT   
  143E7C:  1E F3 03 00 00     CALL_FUNC    modelCategory
  143E81:  26 D2 5C 00 00     ASSIGN       fillInventoryShownModels_local40
  143E86:  19 A9 03 00 00     LINE_NUM     937               ; Code Line 937
  143E8B:  19 AA 03 00 00     LINE_NUM     938               ; Code Line 938
  143E90:  24 D2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local40
  143E95:  01 50 00 00 00     PUSH_INT     80
  143E9A:  14                 NE           
  143E9B:  18 F6 00 00 00     JMP_FALSE    loc_143F92        ; Rel: +0xF6
  143EA0:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143EA5:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  143EAA:  1A                 ARG_COMMIT   
  143EAB:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  143EB0:  26 D3 5C 00 00     ASSIGN       fillInventoryShownModels_local41
  143EB5:  19 AD 03 00 00     LINE_NUM     941               ; Code Line 941
  143EBA:  19 AE 03 00 00     LINE_NUM     942               ; Code Line 942
  143EBF:  01 EE 00 00 00     PUSH_INT     238
  143EC4:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  143EC9:  1A                 ARG_COMMIT   
  143ECA:  24 D2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local40
  143ECF:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  143ED4:  1A                 ARG_COMMIT   
  143ED5:  24 D3 5C 00 00     PUSH_VAR     fillInventoryShownModels_local41
  143EDA:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  143EDF:  1A                 ARG_COMMIT   
  143EE0:  01 C1 BD F0 FF     PUSH_INT     -999999
  143EE5:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  143EEA:  1A                 ARG_COMMIT   
  143EEB:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  143EF0:  26 D4 5C 00 00     ASSIGN       fillInventoryShownModels_local42
  143EF5:  19 AE 03 00 00     LINE_NUM     942               ; Code Line 942
  143EFA:  19 AF 03 00 00     LINE_NUM     943               ; Code Line 943
  143EFF:  24 D4 5C 00 00     PUSH_VAR     fillInventoryShownModels_local42
  143F04:  01 1E 00 00 00     PUSH_INT     30
  143F09:  11                 GE           
  143F0A:  18 87 00 00 00     JMP_FALSE    loc_143F92        ; Rel: +0x87
  143F0F:  24 CE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local36
  143F14:  18 5E 00 00 00     JMP_FALSE    loc_143F73        ; Rel: +0x5E
  143F19:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143F1E:  26 64 10 00 00     ASSIGN       isModelNew_arg0
  143F23:  1A                 ARG_COMMIT   
  143F24:  1E 9B 03 00 00     CALL_FUNC    isModelNew
  143F29:  2D 26 00 00 00     OR_JMP       loc_143F50        ; Rel: +0x26
  143F2E:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143F33:  26 14 11 00 00     ASSIGN       modelUpgrade_arg0
  143F38:  1A                 ARG_COMMIT   
  143F39:  1E FB 03 00 00     CALL_FUNC    modelUpgrade
  143F3E:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143F43:  26 19 11 00 00     ASSIGN       modelPendingUpgrade_arg0
  143F48:  1A                 ARG_COMMIT   
  143F49:  1E FF 03 00 00     CALL_FUNC    modelPendingUpgrade
  143F4E:  10                 LT           
  143F4F:  0E                 LOG_OR       
loc_143F50:
  143F50:  18 22 00 00 00     JMP_FALSE    loc_143F73        ; Rel: +0x22
  143F55:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  143F5A:  26 4B 54 00 00     ASSIGN       inventory_selectedSliderIndex
  143F5F:  19 B5 03 00 00     LINE_NUM     949               ; Code Line 949
  143F64:  01 00 00 00 00     PUSH_INT     0
  143F69:  26 CE 5C 00 00     ASSIGN       fillInventoryShownModels_local36
  143F6E:  19 B6 03 00 00     LINE_NUM     950               ; Code Line 950
loc_143F73:
  143F73:  24 D1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local39
  143F78:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  143F7D:  28                 ARRAY_IDX    
  143F7E:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  143F83:  19 B9 03 00 00     LINE_NUM     953               ; Code Line 953
  143F88:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  143F8D:  19 BA 03 00 00     LINE_NUM     954               ; Code Line 954
loc_143F92:
  143F92:  1C 8F FE FF FF     JMP          loc_143E22        ; Rel: 0x-171
loc_143F97:
  143F97:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143F9C:  26 93 10 00 00     ASSIGN       modelCount_arg0
  143FA1:  1A                 ARG_COMMIT   
  143FA2:  1E A8 03 00 00     CALL_FUNC    modelCount
  143FA7:  26 CF 5C 00 00     ASSIGN       fillInventoryShownModels_local37
  143FAC:  19 C3 03 00 00     LINE_NUM     963               ; Code Line 963
  143FB1:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  143FB6:  18 9D 01 00 00     JMP_FALSE    loc_144154        ; Rel: +0x19D
  143FBB:  01 00 00 00 00     PUSH_INT     0
  143FC0:  26 D0 5C 00 00     ASSIGN       fillInventoryShownModels_local38
  143FC5:  19 C6 03 00 00     LINE_NUM     966               ; Code Line 966
loc_143FCA:
  143FCA:  24 D0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local38
  143FCF:  24 CF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local37
  143FD4:  10                 LT           
  143FD5:  18 7E 01 00 00     JMP_FALSE    loc_144154        ; Rel: +0x17E
  143FDA:  1C 13 00 00 00     JMP          loc_143FEE        ; Rel: +0x13
loc_143FDF:
  143FDF:  22 D0 5C 00 00     PRE_INC      fillInventoryShownModels_local38
  143FE4:  19 C6 03 00 00     LINE_NUM     966               ; Code Line 966
  143FE9:  1C E0 FF FF FF     JMP          loc_143FCA        ; Rel: 0x-20
loc_143FEE:
  143FEE:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  143FF3:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  143FF8:  1A                 ARG_COMMIT   
  143FF9:  24 D0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local38
  143FFE:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  144003:  1A                 ARG_COMMIT   
  144004:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  144009:  26 D5 5C 00 00     ASSIGN       fillInventoryShownModels_local43
  14400E:  19 C8 03 00 00     LINE_NUM     968               ; Code Line 968
  144013:  19 C9 03 00 00     LINE_NUM     969               ; Code Line 969
  144018:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  14401D:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  144022:  1A                 ARG_COMMIT   
  144023:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  144028:  05                 LOG_NOT      
  144029:  18 25 01 00 00     JMP_FALSE    loc_14414F        ; Rel: +0x125
  14402E:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  144033:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  144038:  1A                 ARG_COMMIT   
  144039:  1E F3 03 00 00     CALL_FUNC    modelCategory
  14403E:  26 D6 5C 00 00     ASSIGN       fillInventoryShownModels_local44
  144043:  19 CD 03 00 00     LINE_NUM     973               ; Code Line 973
  144048:  19 CE 03 00 00     LINE_NUM     974               ; Code Line 974
  14404D:  24 D6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local44
  144052:  01 50 00 00 00     PUSH_INT     80
  144057:  14                 NE           
  144058:  18 F6 00 00 00     JMP_FALSE    loc_14414F        ; Rel: +0xF6
  14405D:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  144062:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  144067:  1A                 ARG_COMMIT   
  144068:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  14406D:  26 D7 5C 00 00     ASSIGN       fillInventoryShownModels_local45
  144072:  19 D1 03 00 00     LINE_NUM     977               ; Code Line 977
  144077:  19 D2 03 00 00     LINE_NUM     978               ; Code Line 978
  14407C:  01 EE 00 00 00     PUSH_INT     238
  144081:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  144086:  1A                 ARG_COMMIT   
  144087:  24 D6 5C 00 00     PUSH_VAR     fillInventoryShownModels_local44
  14408C:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  144091:  1A                 ARG_COMMIT   
  144092:  24 D7 5C 00 00     PUSH_VAR     fillInventoryShownModels_local45
  144097:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  14409C:  1A                 ARG_COMMIT   
  14409D:  01 C1 BD F0 FF     PUSH_INT     -999999
  1440A2:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  1440A7:  1A                 ARG_COMMIT   
  1440A8:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  1440AD:  26 D8 5C 00 00     ASSIGN       fillInventoryShownModels_local46
  1440B2:  19 D2 03 00 00     LINE_NUM     978               ; Code Line 978
  1440B7:  19 D3 03 00 00     LINE_NUM     979               ; Code Line 979
  1440BC:  24 D8 5C 00 00     PUSH_VAR     fillInventoryShownModels_local46
  1440C1:  01 1E 00 00 00     PUSH_INT     30
  1440C6:  11                 GE           
  1440C7:  18 87 00 00 00     JMP_FALSE    loc_14414F        ; Rel: +0x87
  1440CC:  24 CE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local36
  1440D1:  18 5E 00 00 00     JMP_FALSE    loc_144130        ; Rel: +0x5E
  1440D6:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  1440DB:  26 64 10 00 00     ASSIGN       isModelNew_arg0
  1440E0:  1A                 ARG_COMMIT   
  1440E1:  1E 9B 03 00 00     CALL_FUNC    isModelNew
  1440E6:  2D 26 00 00 00     OR_JMP       loc_14410D        ; Rel: +0x26
  1440EB:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  1440F0:  26 14 11 00 00     ASSIGN       modelUpgrade_arg0
  1440F5:  1A                 ARG_COMMIT   
  1440F6:  1E FB 03 00 00     CALL_FUNC    modelUpgrade
  1440FB:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  144100:  26 19 11 00 00     ASSIGN       modelPendingUpgrade_arg0
  144105:  1A                 ARG_COMMIT   
  144106:  1E FF 03 00 00     CALL_FUNC    modelPendingUpgrade
  14410B:  10                 LT           
  14410C:  0E                 LOG_OR       
loc_14410D:
  14410D:  18 22 00 00 00     JMP_FALSE    loc_144130        ; Rel: +0x22
  144112:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  144117:  26 4B 54 00 00     ASSIGN       inventory_selectedSliderIndex
  14411C:  19 D9 03 00 00     LINE_NUM     985               ; Code Line 985
  144121:  01 00 00 00 00     PUSH_INT     0
  144126:  26 CE 5C 00 00     ASSIGN       fillInventoryShownModels_local36
  14412B:  19 DA 03 00 00     LINE_NUM     986               ; Code Line 986
loc_144130:
  144130:  24 D5 5C 00 00     PUSH_VAR     fillInventoryShownModels_local43
  144135:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  14413A:  28                 ARRAY_IDX    
  14413B:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  144140:  19 DD 03 00 00     LINE_NUM     989               ; Code Line 989
  144145:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  14414A:  19 DE 03 00 00     LINE_NUM     990               ; Code Line 990
loc_14414F:
  14414F:  1C 8F FE FF FF     JMP          loc_143FDF        ; Rel: 0x-171
loc_144154:
  144154:  1C 09 04 00 00     JMP          loc_14455E        ; Rel: +0x409
loc_144159:
  144159:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  14415E:  26 93 10 00 00     ASSIGN       modelCount_arg0
  144163:  1A                 ARG_COMMIT   
  144164:  1E A8 03 00 00     CALL_FUNC    modelCount
  144169:  26 D9 5C 00 00     ASSIGN       fillInventoryShownModels_local47
  14416E:  19 E8 03 00 00     LINE_NUM     1000              ; Code Line 1000
  144173:  19 E9 03 00 00     LINE_NUM     1001              ; Code Line 1001
  144178:  19 EA 03 00 00     LINE_NUM     1002              ; Code Line 1002
  14417D:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  144182:  18 3E 01 00 00     JMP_FALSE    loc_1442C1        ; Rel: +0x13E
  144187:  01 00 00 00 00     PUSH_INT     0
  14418C:  26 DA 5C 00 00     ASSIGN       fillInventoryShownModels_local48
  144191:  19 ED 03 00 00     LINE_NUM     1005              ; Code Line 1005
loc_144196:
  144196:  24 DA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local48
  14419B:  24 D9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local47
  1441A0:  10                 LT           
  1441A1:  18 1F 01 00 00     JMP_FALSE    loc_1442C1        ; Rel: +0x11F
  1441A6:  1C 13 00 00 00     JMP          loc_1441BA        ; Rel: +0x13
loc_1441AB:
  1441AB:  22 DA 5C 00 00     PRE_INC      fillInventoryShownModels_local48
  1441B0:  19 ED 03 00 00     LINE_NUM     1005              ; Code Line 1005
  1441B5:  1C E0 FF FF FF     JMP          loc_144196        ; Rel: 0x-20
loc_1441BA:
  1441BA:  24 AD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local3
  1441BF:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  1441C4:  1A                 ARG_COMMIT   
  1441C5:  24 DA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local48
  1441CA:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  1441CF:  1A                 ARG_COMMIT   
  1441D0:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  1441D5:  26 DB 5C 00 00     ASSIGN       fillInventoryShownModels_local49
  1441DA:  19 EF 03 00 00     LINE_NUM     1007              ; Code Line 1007
  1441DF:  19 F0 03 00 00     LINE_NUM     1008              ; Code Line 1008
  1441E4:  24 DB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local49
  1441E9:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  1441EE:  1A                 ARG_COMMIT   
  1441EF:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  1441F4:  05                 LOG_NOT      
  1441F5:  18 C6 00 00 00     JMP_FALSE    loc_1442BC        ; Rel: +0xC6
  1441FA:  24 DB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local49
  1441FF:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  144204:  1A                 ARG_COMMIT   
  144205:  1E F3 03 00 00     CALL_FUNC    modelCategory
  14420A:  26 DC 5C 00 00     ASSIGN       fillInventoryShownModels_local50
  14420F:  19 F4 03 00 00     LINE_NUM     1012              ; Code Line 1012
  144214:  19 F5 03 00 00     LINE_NUM     1013              ; Code Line 1013
  144219:  24 DC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local50
  14421E:  24 AF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local5
  144223:  0D                 EQ           
  144224:  2C 1B 00 00 00     AND_JMP      loc_144240        ; Rel: +0x1B
  144229:  24 DB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local49
  14422E:  26 45 11 00 00     ASSIGN       modelLight_arg0
  144233:  1A                 ARG_COMMIT   
  144234:  1E 19 04 00 00     CALL_FUNC    modelLight
  144239:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  14423E:  0F                 GT           
  14423F:  15                 LOG_AND      
loc_144240:
  144240:  18 7B 00 00 00     JMP_FALSE    loc_1442BC        ; Rel: +0x7B
  144245:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  14424A:  01 FF FF FF FF     PUSH_INT     -1
  14424F:  0D                 EQ           
  144250:  2D 47 00 00 00     OR_JMP       loc_144298        ; Rel: +0x47
  144255:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  14425A:  01 1E 02 00 00     PUSH_INT     542
  14425F:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  144264:  1A                 ARG_COMMIT   
  144265:  24 DC 5C 00 00     PUSH_VAR     fillInventoryShownModels_local50
  14426A:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  14426F:  1A                 ARG_COMMIT   
  144270:  24 DB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local49
  144275:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  14427A:  1A                 ARG_COMMIT   
  14427B:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  144280:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  144285:  1A                 ARG_COMMIT   
  144286:  01 C1 BD F0 FF     PUSH_INT     -999999
  14428B:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  144290:  1A                 ARG_COMMIT   
  144291:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  144296:  0D                 EQ           
  144297:  0E                 LOG_OR       
loc_144298:
  144298:  18 23 00 00 00     JMP_FALSE    loc_1442BC        ; Rel: +0x23
  14429D:  24 DB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local49
  1442A2:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  1442A7:  28                 ARRAY_IDX    
  1442A8:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  1442AD:  19 FA 03 00 00     LINE_NUM     1018              ; Code Line 1018
  1442B2:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  1442B7:  19 FB 03 00 00     LINE_NUM     1019              ; Code Line 1019
loc_1442BC:
  1442BC:  1C EE FE FF FF     JMP          loc_1441AB        ; Rel: 0x-112
loc_1442C1:
  1442C1:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  1442C6:  26 93 10 00 00     ASSIGN       modelCount_arg0
  1442CB:  1A                 ARG_COMMIT   
  1442CC:  1E A8 03 00 00     CALL_FUNC    modelCount
  1442D1:  26 D9 5C 00 00     ASSIGN       fillInventoryShownModels_local47
  1442D6:  19 04 04 00 00     LINE_NUM     1028              ; Code Line 1028
  1442DB:  01 00 00 00 00     PUSH_INT     0
  1442E0:  26 DA 5C 00 00     ASSIGN       fillInventoryShownModels_local48
  1442E5:  19 05 04 00 00     LINE_NUM     1029              ; Code Line 1029
loc_1442EA:
  1442EA:  24 DA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local48
  1442EF:  24 D9 5C 00 00     PUSH_VAR     fillInventoryShownModels_local47
  1442F4:  10                 LT           
  1442F5:  18 68 02 00 00     JMP_FALSE    loc_14455E        ; Rel: +0x268
  1442FA:  1C 13 00 00 00     JMP          loc_14430E        ; Rel: +0x13
loc_1442FF:
  1442FF:  22 DA 5C 00 00     PRE_INC      fillInventoryShownModels_local48
  144304:  19 05 04 00 00     LINE_NUM     1029              ; Code Line 1029
  144309:  1C E0 FF FF FF     JMP          loc_1442EA        ; Rel: 0x-20
loc_14430E:
  14430E:  24 AE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local4
  144313:  26 9E 10 00 00     ASSIGN       modelBaseKey_arg0
  144318:  1A                 ARG_COMMIT   
  144319:  24 DA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local48
  14431E:  26 9F 10 00 00     ASSIGN       modelBaseKey_arg1
  144323:  1A                 ARG_COMMIT   
  144324:  1E AD 03 00 00     CALL_FUNC    modelBaseKey
  144329:  26 DD 5C 00 00     ASSIGN       fillInventoryShownModels_local51
  14432E:  19 07 04 00 00     LINE_NUM     1031              ; Code Line 1031
  144333:  19 08 04 00 00     LINE_NUM     1032              ; Code Line 1032
  144338:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  14433D:  26 C5 11 00 00     ASSIGN       isModelEmpty_arg0
  144342:  1A                 ARG_COMMIT   
  144343:  1E 73 04 00 00     CALL_FUNC    isModelEmpty
  144348:  05                 LOG_NOT      
  144349:  2C 1B 00 00 00     AND_JMP      loc_144365        ; Rel: +0x1B
  14434E:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  144353:  26 45 11 00 00     ASSIGN       modelLight_arg0
  144358:  1A                 ARG_COMMIT   
  144359:  1E 19 04 00 00     CALL_FUNC    modelLight
  14435E:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  144363:  0F                 GT           
  144364:  15                 LOG_AND      
loc_144365:
  144365:  18 F3 01 00 00     JMP_FALSE    loc_144559        ; Rel: +0x1F3
  14436A:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  14436F:  26 09 11 00 00     ASSIGN       modelCategory_arg0
  144374:  1A                 ARG_COMMIT   
  144375:  1E F3 03 00 00     CALL_FUNC    modelCategory
  14437A:  26 DE 5C 00 00     ASSIGN       fillInventoryShownModels_local52
  14437F:  19 0C 04 00 00     LINE_NUM     1036              ; Code Line 1036
  144384:  19 0D 04 00 00     LINE_NUM     1037              ; Code Line 1037
  144389:  24 DE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local52
  14438E:  24 AF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local5
  144393:  0D                 EQ           
  144394:  2C 1B 00 00 00     AND_JMP      loc_1443B0        ; Rel: +0x1B
  144399:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  14439E:  26 45 11 00 00     ASSIGN       modelLight_arg0
  1443A3:  1A                 ARG_COMMIT   
  1443A4:  1E 19 04 00 00     CALL_FUNC    modelLight
  1443A9:  24 2D 5C 00 00     PUSH_VAR     lightFilterValue
  1443AE:  11                 GE           
  1443AF:  15                 LOG_AND      
loc_1443B0:
  1443B0:  18 A8 01 00 00     JMP_FALSE    loc_144559        ; Rel: +0x1A8
  1443B5:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  1443BA:  01 FF FF FF FF     PUSH_INT     -1
  1443BF:  0D                 EQ           
  1443C0:  2D 47 00 00 00     OR_JMP       loc_144408        ; Rel: +0x47
  1443C5:  24 AA 5C 00 00     PUSH_VAR     fillInventoryShownModels_local0
  1443CA:  01 1E 02 00 00     PUSH_INT     542
  1443CF:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  1443D4:  1A                 ARG_COMMIT   
  1443D5:  24 DE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local52
  1443DA:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  1443DF:  1A                 ARG_COMMIT   
  1443E0:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  1443E5:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  1443EA:  1A                 ARG_COMMIT   
  1443EB:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  1443F0:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  1443F5:  1A                 ARG_COMMIT   
  1443F6:  01 C1 BD F0 FF     PUSH_INT     -999999
  1443FB:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  144400:  1A                 ARG_COMMIT   
  144401:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  144406:  0D                 EQ           
  144407:  0E                 LOG_OR       
loc_144408:
  144408:  18 50 01 00 00     JMP_FALSE    loc_144559        ; Rel: +0x150
  14440D:  01 01 00 00 00     PUSH_INT     1
  144412:  26 DF 5C 00 00     ASSIGN       fillInventoryShownModels_local53
  144417:  19 11 04 00 00     LINE_NUM     1041              ; Code Line 1041
  14441C:  19 12 04 00 00     LINE_NUM     1042              ; Code Line 1042
  144421:  24 AB 5C 00 00     PUSH_VAR     fillInventoryShownModels_local1
  144426:  05                 LOG_NOT      
  144427:  18 08 01 00 00     JMP_FALSE    loc_144530        ; Rel: +0x108
  14442C:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  144431:  26 11 11 00 00     ASSIGN       modelTemplateIndex_arg0
  144436:  1A                 ARG_COMMIT   
  144437:  1E F9 03 00 00     CALL_FUNC    modelTemplateIndex
  14443C:  26 E0 5C 00 00     ASSIGN       fillInventoryShownModels_local54
  144441:  19 15 04 00 00     LINE_NUM     1045              ; Code Line 1045
  144446:  19 16 04 00 00     LINE_NUM     1046              ; Code Line 1046
  14444B:  01 EE 00 00 00     PUSH_INT     238
  144450:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  144455:  1A                 ARG_COMMIT   
  144456:  24 DE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local52
  14445B:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  144460:  1A                 ARG_COMMIT   
  144461:  24 E0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local54
  144466:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  14446B:  1A                 ARG_COMMIT   
  14446C:  01 C1 BD F0 FF     PUSH_INT     -999999
  144471:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  144476:  1A                 ARG_COMMIT   
  144477:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  14447C:  26 E1 5C 00 00     ASSIGN       fillInventoryShownModels_local55
  144481:  19 16 04 00 00     LINE_NUM     1046              ; Code Line 1046
  144486:  19 17 04 00 00     LINE_NUM     1047              ; Code Line 1047
  14448B:  01 44 01 00 00     PUSH_INT     324
  144490:  26 66 0D 00 00     ASSIGN       getEquipmentByCategory_arg0
  144495:  1A                 ARG_COMMIT   
  144496:  24 DE 5C 00 00     PUSH_VAR     fillInventoryShownModels_local52
  14449B:  26 67 0D 00 00     ASSIGN       getEquipmentByCategory_arg1
  1444A0:  1A                 ARG_COMMIT   
  1444A1:  24 E0 5C 00 00     PUSH_VAR     fillInventoryShownModels_local54
  1444A6:  26 68 0D 00 00     ASSIGN       getEquipmentByCategory_arg2
  1444AB:  1A                 ARG_COMMIT   
  1444AC:  01 C1 BD F0 FF     PUSH_INT     -999999
  1444B1:  26 69 0D 00 00     ASSIGN       getEquipmentByCategory_arg3
  1444B6:  1A                 ARG_COMMIT   
  1444B7:  1E 0B 02 00 00     CALL_FUNC    getEquipmentByCategory
  1444BC:  26 E2 5C 00 00     ASSIGN       fillInventoryShownModels_local56
  1444C1:  19 17 04 00 00     LINE_NUM     1047              ; Code Line 1047
  1444C6:  19 18 04 00 00     LINE_NUM     1048              ; Code Line 1048
  1444CB:  24 E1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local55
  1444D0:  01 00 00 00 00     PUSH_INT     0
  1444D5:  0F                 GT           
  1444D6:  2C 10 00 00 00     AND_JMP      loc_1444E7        ; Rel: +0x10
  1444DB:  24 E1 5C 00 00     PUSH_VAR     fillInventoryShownModels_local55
  1444E0:  01 1E 00 00 00     PUSH_INT     30
  1444E5:  10                 LT           
  1444E6:  15                 LOG_AND      
loc_1444E7:
  1444E7:  2C 10 00 00 00     AND_JMP      loc_1444F8        ; Rel: +0x10
  1444EC:  24 E2 5C 00 00     PUSH_VAR     fillInventoryShownModels_local56
  1444F1:  01 0B 00 00 00     PUSH_INT     11
  1444F6:  14                 NE           
  1444F7:  15                 LOG_AND      
loc_1444F8:
  1444F8:  26 DF 5C 00 00     ASSIGN       fillInventoryShownModels_local53
  1444FD:  19 19 04 00 00     LINE_NUM     1049              ; Code Line 1049
  144502:  24 DF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local53
  144507:  18 28 00 00 00     JMP_FALSE    loc_144530        ; Rel: +0x28
  14450C:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  144511:  26 1A 2A 00 00     ASSIGN       isModelInAnySet_arg0
  144516:  1A                 ARG_COMMIT   
  144517:  1E C5 08 00 00     CALL_FUNC    isModelInAnySet
  14451C:  18 13 00 00 00     JMP_FALSE    loc_144530        ; Rel: +0x13
  144521:  01 00 00 00 00     PUSH_INT     0
  144526:  26 DF 5C 00 00     ASSIGN       fillInventoryShownModels_local53
  14452B:  19 1D 04 00 00     LINE_NUM     1053              ; Code Line 1053
loc_144530:
  144530:  24 DF 5C 00 00     PUSH_VAR     fillInventoryShownModels_local53
  144535:  18 23 00 00 00     JMP_FALSE    loc_144559        ; Rel: +0x23
  14453A:  24 DD 5C 00 00     PUSH_VAR     fillInventoryShownModels_local51
  14453F:  24 2C 5C 00 00     PUSH_VAR     inventoryShownModelsNumbersCount
  144544:  28                 ARRAY_IDX    
  144545:  26 5C 54 00 00     ASSIGN       inventoryShownModels
  14454A:  19 22 04 00 00     LINE_NUM     1058              ; Code Line 1058
  14454F:  22 2C 5C 00 00     PRE_INC      inventoryShownModelsNumbersCount
  144554:  19 23 04 00 00     LINE_NUM     1059              ; Code Line 1059
loc_144559:
  144559:  1C A5 FD FF FF     JMP          loc_1442FF        ; Rel: 0x-25B
loc_14455E:
  14455E:  1F                 RET                            ; mark end of function
;Function fillInventoryShownModels() End
; ------------------------------------------------------------

```

