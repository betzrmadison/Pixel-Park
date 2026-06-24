package com.pixelpark;

import org.bukkit.entity.Minecart;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.vehicle.VehicleMoveEvent;
import org.bukkit.util.Vector;

// Listens to track ride telemetry
public class RideTelemetryListener implements Listener {
    @EventHandler
    public void onMinecartMove(VehicleMoveEvent event) {
        // Check if the vehicle moving is actually a Minecart
        if (event.getVehicle() instanceof Minecart) {
            Minecart cart = (Minecart) event.getVehicle();

            // Grab coordinates
            double x = cart.getLocation().getX();
            double y = cart.getLocation().getY();
            double z = cart.getLocation().getZ();

            // Calculate speed
            Vector velocity = cart.getVelocity();
            double speed = velocity.length();

            // Print data
            System.out.printf("[Telemetry] Cart ID: %s | Pos: %.2f, %.2f, %.2f | Speed %.2f m/s%n",
                    cart.getUniqueId().toString().substring(0, 8), x, y, z, speed);
        }
    }
}
