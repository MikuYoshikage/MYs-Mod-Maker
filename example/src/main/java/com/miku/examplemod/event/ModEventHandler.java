package {{PACKAGE_NAME}}.event;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.minecraftforge.event.LootTableLoadEvent;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import {{PACKAGE_NAME}}.ExampleMod;
import {{PACKAGE_NAME}}.item.ModItems;

import java.util.List;
import java.util.Random;

@Mod.EventBusSubscriber(modid = "{{MOD_ID}}")
public class ModEventHandler {

    private static final Random RANDOM = new Random();
    private static final float VILLAGER_DROP_CHANCE = 0.5f; // шанс дропу з жителя

    // --- Дроп з жителя при смерті ---
    @SubscribeEvent
    public static void onLivingDrops(LivingDropsEvent event) {
        if (!(event.getEntity() instanceof Villager villager)) {
            return;
        }
        if (RANDOM.nextFloat() > VILLAGER_DROP_CHANCE) {
            return;
        }

        String randomId = randomTrackId();
        ItemStack recordStack = new ItemStack(ModItems.RECORD_ITEMS.get(randomId).get());

        ItemEntity itemEntity = new ItemEntity(
                villager.level(),
                villager.getX(), villager.getY(), villager.getZ(),
                recordStack
        );
        event.getDrops().add(itemEntity);
    }

    // --- Спавн у скринях сіл ---
    @SubscribeEvent
    public static void onLootTableLoad(LootTableLoadEvent event) {
        ResourceLocation tableId = event.getName();

        // спрацьовує лише для loot table сіл (village_*)
        if (tableId.getNamespace().equals("minecraft")
                && tableId.getPath().startsWith("chests/village/")) {

            String randomId = randomTrackId();

            LootPool pool = LootPool.lootPool()
                    .setRolls(ConstantValue.exactly(1))
                    .add(LootItem.lootTableItem(ModItems.RECORD_ITEMS.get(randomId).get())
                            .setWeight(2)) // низька вага = рідкісний предмет серед іншого лута
                    .build();

            event.getTable().addPool(pool);
        }
    }

    private static String randomTrackId() {
        List<String> trackIds = List.of(ExampleMod.TRACK_IDS);
        return trackIds.get(RANDOM.nextInt(trackIds.size()));
    }
}