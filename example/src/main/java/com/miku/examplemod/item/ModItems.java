package {{PACKAGE_NAME}}.item;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.RecordItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import {{PACKAGE_NAME}}.ExampleMod;
import {{PACKAGE_NAME}}.sound.ModSounds;

import java.util.LinkedHashMap;
import java.util.Map;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, ExampleMod.MODID);

    public static final Map<String, RegistryObject<Item>> RECORD_ITEMS = new LinkedHashMap<>();

    static {
        for (String id : ExampleMod.TRACK_IDS) {
            String itemId = "record_" + id;
            RECORD_ITEMS.put(id, ITEMS.register(itemId, () -> new RecordItem(
                    12,
                    ModSounds.RECORDS.get(id).get(),
                    new Item.Properties().stacksTo(1).rarity(Rarity.RARE),
                    18000
            )));
        }
    }
}