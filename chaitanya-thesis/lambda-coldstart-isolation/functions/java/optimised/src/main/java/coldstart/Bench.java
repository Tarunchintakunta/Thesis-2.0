package coldstart;

import java.util.List;
import java.util.Map;

/**
 * Local init benchmark entry point (scripts/local_init_bench.py).
 * Prints wall-clock timestamps (epoch microseconds) after the handler class is
 * initialised and after one invocation, plus the digest for the equality check.
 * Usage: java -cp function.jar coldstart.Bench <seed> <iterations> <items comma separated>
 */
public class Bench {
    public static void main(String[] args) throws Exception {
        Class.forName("coldstart.Handler");  // force static init (loads the dependencies in the default variant)
        Handler handler = new Handler();
        long initDone = nowMicros();
        List<Integer> items = args.length > 2 && !args[2].isEmpty()
                ? java.util.Arrays.stream(args[2].split(",")).map(Integer::valueOf).toList()
                : List.of();
        Map<String, Object> out = handler.handleRequest(Map.of(
                "seed", args[0], "iterations", Integer.parseInt(args[1]), "items", items));
        long done = nowMicros();
        System.out.println("{\"t_init_us\": " + initDone + ", \"t_done_us\": " + done
                + ", \"digest\": \"" + out.get("digest") + "\", \"items_total\": " + out.get("items_total") + "}");
    }

    static long nowMicros() {
        java.time.Instant i = java.time.Instant.now();
        return i.getEpochSecond() * 1_000_000L + i.getNano() / 1_000L;
    }
}
