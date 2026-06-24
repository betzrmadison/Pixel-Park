package com.pixelpark;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.EventHandler;

// Entry point for plugin
public class PixelParkCore extends JavaPlugin {

    // This runs when the Minecraft server starts up
    @Override
    public void onEnable() {
        getLogger().info("Pixel Park Core has booted up successfully!!");
        getServer().getPluginManager().registerEvents(new RideTelemetryListener(), this);
    }

    // This runs when the Minecraft server is stopped
    @EventHandler
    public void onDisable() {
        getLogger().info("Pixel Park Core shutting down.");
    }
}