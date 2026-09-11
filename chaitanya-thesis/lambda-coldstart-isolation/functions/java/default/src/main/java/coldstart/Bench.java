package coldstart;

import java.util.List;
import java.util.Map;

/**
 * Local init benchmark entry point (same as the optimised variant's).
 * Usage: java -cp function.jar coldstart.Bench <seed> <iterations> <items comma separated>
 */
public class Bench {
    public static void main(String[] args) throws Exception {
        Class.forName("coldstart.Handler");  // static init pulls in Jackson, Guava, commons-lang3
        Handler handler = new Handler();
        long initDone = nowMicros();
        List<Integer> items = args.length > 2 && !args[2].isEmpty()
                ? java.util.Arrays.stream(args[2].split(",")).map(Integer::valueOf).toList()
                : List.of();
        Map<String, Object> out = handler.handleRequest(Map.of(
                "seed", args[0], "iterations", Integer.parseInt(args[1]), "items", items));
        long done = nowMicros();
        System.out.println("{\"t_init_us\": " + initDone + ", \"t_done_us\": " + done
                + ", \"digest\": \"" + out.get("digest") + "\", \"items_total\": " + out.get("items_total")
                + ", \"touched\": " + Handler.touched() + "}");
    }

    static long nowMicros() {
        java.time.Instant i = java.time.Instant.now();
        return i.getEpochSecond() * 1_000_000L + i.getNano() / 1_000L;
    }
}
