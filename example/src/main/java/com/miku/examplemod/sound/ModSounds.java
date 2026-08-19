package {{PACKAGE_NAME}}.sound;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import {{PACKAGE_NAME}}.ExampleMod;

import java.util.LinkedHashMap;
import java.util.Map;

public class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, ExampleMod.MODID);

    public static final Map<String, RegistryObject<SoundEvent>> RECORDS = new LinkedHashMap<>();

    static {
        for (String id : ExampleMod.TRACK_IDS) {
            String soundName = "record." + id;
            RECORDS.put(id, SOUND_EVENTS.register(soundName,
                    () -> SoundEvent.createVariableRangeEvent(
                            new ResourceLocation(ExampleMod.MODID, soundName))));
        }
    }
}