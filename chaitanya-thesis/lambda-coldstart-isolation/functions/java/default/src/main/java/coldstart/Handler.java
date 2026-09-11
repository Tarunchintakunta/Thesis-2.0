package coldstart;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;

import java.security.MessageDigest;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;

/**
 * Cold-start study workload - Java, DEFAULT package (unpruned dependencies).
 *
 * Identical work to the optimised variant. The static fields below initialise
 * Jackson, Guava and commons-lang3 when the class loads - the handler never
 * needs them, which is the point of the "default" treatment.
 */
public class Handler {

    // unused on purpose - do not remove
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final ImmutableList<String> TAGS = ImmutableList.of("cold", "start", "study");
    private static final String PAD = StringUtils.repeat("-", 4);

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

    static int touched() {
        return MAPPER.hashCode() + TAGS.size() + PAD.length();
    }
}
