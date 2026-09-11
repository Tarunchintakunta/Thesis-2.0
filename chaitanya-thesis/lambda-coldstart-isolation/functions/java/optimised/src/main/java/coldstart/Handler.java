package coldstart;

import java.security.MessageDigest;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;

/**
 * Cold-start study workload - Java, OPTIMISED package (no dependencies).
 *
 * Handler string: coldstart.Handler::handleRequest. The Lambda runtime turns the
 * JSON event into a Map, so no JSON library is needed here. Same work as the
 * Python and Node.js versions: iterated SHA-256 + count/sum of the items.
 */
public class Handler {

    public static String digest(String seed, int n) throws Exception {
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        byte[] h = seed.getBytes(java.nio.charset.StandardCharsets.UTF_8);
        for (int i = 0; i < n; i++) {
            h = sha.digest(h);
        }
        return HexFormat.of().formatHex(h);
    }

    public Map<String, Object> handleRequest(Map<String, Object> event) throws Exception {
        Map<String, Object> out = new HashMap<>();
        if (Boolean.TRUE.equals(event.get("warmer"))) {
            out.put("ok", true);
            out.put("warmer", true);
            return out;
        }
        int n = ((Number) event.getOrDefault("iterations", 1000)).intValue();
        List<?> items = (List<?>) event.getOrDefault("items", List.of());
        long total = 0;
        for (Object o : items) {
            total += ((Number) o).longValue();
        }
        out.put("ok", true);
        out.put("digest", digest(String.valueOf(event.getOrDefault("seed", "thesis")), n));
        out.put("n", n);
        out.put("items", items.size());
        out.put("items_total", total);
        return out;
    }
}
