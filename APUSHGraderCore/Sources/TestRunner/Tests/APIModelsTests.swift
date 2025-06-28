import Foundation
import APUSHGraderCore

public struct APIModelsTests: TestRunnable {
    public init() {}
    
    public func runTests() -> TestSuite {
        let suite = TestSuite("APIModels")
        
        // APIConfig Static Properties Tests
        suite.addTest("API Config Defaults") {
            suite.assertEqual(APIConfig.temperature, 0.3, "API temperature setting")
            suite.assertEqual(APIConfig.maxTokens, 1500, "API max tokens setting")
            suite.assertEqual(APIConfig.timeoutInterval, 30.0, "API timeout setting")
            suite.assertEqual(APIConfig.preferredModel, .claude35Sonnet, "Preferred model setting")
        }
        
        // Model Name Tests
        suite.addTest("OpenAI Model Names") {
            suite.assertEqual(APIConfig.Model.gpt4o.name, "gpt-4o", "GPT-4o model name")
            suite.assertEqual(APIConfig.Model.gpt4oMini.name, "gpt-4o-mini", "GPT-4o Mini model name")
        }
        
        suite.addTest("Anthropic Model Names") {
            suite.assertEqual(APIConfig.Model.claude35Sonnet.name, "claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet model name")
            suite.assertEqual(APIConfig.Model.claude3Haiku.name, "claude-3-haiku-20240307", "Claude 3 Haiku model name")
        }
        
        // Provider Mapping Tests
        suite.addTest("OpenAI Provider Mapping") {
            suite.assertEqual(APIConfig.Model.gpt4o.provider, .openai, "GPT-4o provider mapping")
            suite.assertEqual(APIConfig.Model.gpt4oMini.provider, .openai, "GPT-4o Mini provider mapping")
        }
        
        suite.addTest("Anthropic Provider Mapping") {
            suite.assertEqual(APIConfig.Model.claude35Sonnet.provider, .anthropic, "Claude 3.5 Sonnet provider mapping")
            suite.assertEqual(APIConfig.Model.claude3Haiku.provider, .anthropic, "Claude 3 Haiku provider mapping")
        }
        
        // Provider Enum Tests
        suite.addTest("Provider Enum Cases") {
            let openaiProvider: APIConfig.Provider = .openai
            let anthropicProvider: APIConfig.Provider = .anthropic
            
            suite.assert(openaiProvider != anthropicProvider, "Providers are distinct")
        }
        
        // Model Enum Tests
        suite.addTest("Model Enum Cases") {
            let gpt4o: APIConfig.Model = .gpt4o
            let gpt4oMini: APIConfig.Model = .gpt4oMini
            let claude35Sonnet: APIConfig.Model = .claude35Sonnet
            let claude3Haiku: APIConfig.Model = .claude3Haiku
            
            suite.assert(gpt4o != gpt4oMini, "GPT models are distinct")
            suite.assert(claude35Sonnet != claude3Haiku, "Claude models are distinct")
            suite.assert(gpt4o != claude35Sonnet, "Cross-provider models are distinct")
        }
        
        // Configuration Consistency Tests
        suite.addTest("Preferred Model Is Valid") {
            let preferredModel = APIConfig.preferredModel
            
            suite.assert(!preferredModel.name.isEmpty, "Preferred model has non-empty name")
            
            let provider = preferredModel.provider
            suite.assert(provider == .openai || provider == .anthropic, "Preferred model has valid provider")
        }
        
        suite.addTest("All Models Have Valid Names") {
            let models: [APIConfig.Model] = [.gpt4o, .gpt4oMini, .claude35Sonnet, .claude3Haiku]
            
            for model in models {
                suite.assert(!model.name.isEmpty, "Model \(model) has non-empty name")
            }
        }
        
        suite.addTest("All Models Have Valid Providers") {
            let models: [APIConfig.Model] = [.gpt4o, .gpt4oMini, .claude35Sonnet, .claude3Haiku]
            
            for model in models {
                let provider = model.provider
                suite.assert(provider == .openai || provider == .anthropic, "Model \(model) has valid provider")
            }
        }
        
        // Configuration Range Tests
        suite.addTest("Configuration Ranges") {
            // Temperature should be reasonable for AI models (0.0 - 2.0)
            suite.assert(APIConfig.temperature >= 0.0, "Temperature is non-negative")
            suite.assert(APIConfig.temperature <= 2.0, "Temperature is within reasonable range")
            
            // Max tokens should be positive and reasonable
            suite.assert(APIConfig.maxTokens > 0, "Max tokens is positive")
            suite.assert(APIConfig.maxTokens <= 10000, "Max tokens is within reasonable range")
            
            // Timeout should be positive and reasonable (not too short or too long)
            suite.assert(APIConfig.timeoutInterval > 0.0, "Timeout is positive")
            suite.assert(APIConfig.timeoutInterval <= 300.0, "Timeout is within reasonable range")
        }
        
        // Model Name Format Tests
        suite.addTest("Model Name Formats") {
            // OpenAI models should follow expected naming pattern
            suite.assert(APIConfig.Model.gpt4o.name.hasPrefix("gpt-"), "GPT-4o follows naming convention")
            suite.assert(APIConfig.Model.gpt4oMini.name.hasPrefix("gpt-"), "GPT-4o Mini follows naming convention")
            
            // Anthropic models should follow expected naming pattern
            suite.assert(APIConfig.Model.claude35Sonnet.name.hasPrefix("claude-"), "Claude 3.5 Sonnet follows naming convention")
            suite.assert(APIConfig.Model.claude3Haiku.name.hasPrefix("claude-"), "Claude 3 Haiku follows naming convention")
            
            // Should include version dates
            suite.assert(APIConfig.Model.claude35Sonnet.name.contains("20241022"), "Claude 3.5 Sonnet includes version date")
            suite.assert(APIConfig.Model.claude3Haiku.name.contains("20240307"), "Claude 3 Haiku includes version date")
        }
        
        suite.run()
        return suite
    }
}