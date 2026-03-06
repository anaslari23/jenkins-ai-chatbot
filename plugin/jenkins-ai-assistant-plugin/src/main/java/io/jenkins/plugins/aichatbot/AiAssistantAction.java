package io.jenkins.plugins.aichatbot;

import hudson.Extension;
import hudson.model.RootAction;
import org.kohsuke.stapler.StaplerRequest;
import org.kohsuke.stapler.StaplerResponse;
import org.kohsuke.stapler.verb.POST;
import org.kohsuke.stapler.interceptor.RequirePOST;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import javax.servlet.ServletException;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Jenkins AI Assistant Plugin
 *
 * Adds an AI chatbot panel to the Jenkins dashboard that communicates
 * with the FastAPI backend to answer Jenkins-related questions.
 */
@Extension
public class AiAssistantAction implements RootAction {

    private static final Logger LOGGER = Logger.getLogger(AiAssistantAction.class.getName());
    private static final String BACKEND_URL = System.getProperty(
            "ai.assistant.backend.url",
            "http://localhost:8000"
    );
    private static final Gson GSON = new Gson();

    @Override
    public String getIconFileName() {
        return "symbol-chat";
    }

    @Override
    public String getDisplayName() {
        return "AI Assistant";
    }

    @Override
    public String getUrlName() {
        return "ai-assistant";
    }

    /**
     * Proxy endpoint: receives a question from the Jenkins UI
     * and forwards it to the FastAPI backend.
     */
    @RequirePOST
    public void doAsk(StaplerRequest req, StaplerResponse rsp)
            throws ServletException, IOException {

        rsp.setContentType("application/json;charset=UTF-8");
        PrintWriter writer = rsp.getWriter();

        try {
            // Parse incoming request
            StringBuilder body = new StringBuilder();
            String line;
            while ((line = req.getReader().readLine()) != null) {
                body.append(line);
            }

            JsonObject requestJson = GSON.fromJson(body.toString(), JsonObject.class);
            String question = requestJson.get("question").getAsString();

            // Forward to backend
            String backendResponse = callBackend(question);
            writer.write(backendResponse);

        } catch (Exception e) {
            LOGGER.log(Level.WARNING, "AI Assistant error", e);
            JsonObject error = new JsonObject();
            error.addProperty("answer", "Sorry, I encountered an error: " + e.getMessage());
            error.add("sources", GSON.toJsonTree(new String[]{}));
            writer.write(GSON.toJson(error));
        }

        writer.flush();
    }

    /**
     * Call the FastAPI backend /ask endpoint.
     */
    private String callBackend(String question) throws IOException {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpPost httpPost = new HttpPost(BACKEND_URL + "/ask");
            httpPost.setHeader("Content-Type", "application/json");

            JsonObject payload = new JsonObject();
            payload.addProperty("question", question);
            httpPost.setEntity(new StringEntity(GSON.toJson(payload), "UTF-8"));

            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                return EntityUtils.toString(response.getEntity(), "UTF-8");
            }
        }
    }
}
