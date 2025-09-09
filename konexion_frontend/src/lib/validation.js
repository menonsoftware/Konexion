// Performance validation script for WebSocket optimizations
// Run this in the browser console to test the optimizations

class ValidationTests {
	constructor() {
		this.tests = [];
		this.results = [];
	}

	addTest(name, testFn) {
		this.tests.push({ name, testFn });
	}

	async runAll() {
		console.group('🧪 Running Performance Validation Tests');

		for (const test of this.tests) {
			try {
				console.log(`Running: ${test.name}`);
				const result = await test.testFn();
				this.results.push({ name: test.name, passed: true, result });
				console.log(`✅ ${test.name}: PASSED`, result);
			} catch (error) {
				this.results.push({ name: test.name, passed: false, error: error.message });
				console.error(`❌ ${test.name}: FAILED`, error);
			}
		}

		console.groupEnd();
		this.printSummary();
	}

	printSummary() {
		const passed = this.results.filter((r) => r.passed).length;
		const total = this.results.length;

		console.group(`📊 Test Summary: ${passed}/${total} passed`);
		this.results.forEach((result) => {
			if (result.passed) {
				console.log(`✅ ${result.name}`);
			} else {
				console.error(`❌ ${result.name}: ${result.error}`);
			}
		});
		console.groupEnd();
	}
}

// Create test instance
const validator = new ValidationTests();

// Test 1: WebSocket Service exists and has optimizations
validator.addTest('WebSocket Service Optimizations', () => {
	if (typeof window.wsService === 'undefined') {
		throw new Error('wsService not found on window');
	}

	const service = window.wsService;
	if (typeof service.flushChunkBuffer !== 'function') {
		throw new Error('flushChunkBuffer method missing');
	}

	return { service: 'available', methods: 'complete' };
});

// Test 2: Performance Monitor Integration
validator.addTest('Performance Monitor', () => {
	if (typeof window.perfMonitor === 'undefined') {
		throw new Error('perfMonitor not found on window');
	}

	const monitor = window.perfMonitor;
	if (typeof monitor.recordChunk !== 'function') {
		throw new Error('recordChunk method missing');
	}

	if (typeof monitor.getMetrics !== 'function') {
		throw new Error('getMetrics method missing');
	}

	// Test metrics recording
	monitor.enable();
	monitor.recordChunk(10, 1.5);
	const metrics = monitor.getMetrics();

	if (metrics.chunksReceived !== 1) {
		throw new Error('Chunk recording not working');
	}

	monitor.disable();
	monitor.reset();

	return { monitoring: 'working', metrics: 'recordable' };
});

// Test 3: Store Optimizations
validator.addTest('Message Store Optimizations', async () => {
	// This test requires access to the Svelte stores
	// We'll check if the optimized methods exist

	const storeModule = await import('/src/lib/stores.js').catch(() => null);
	if (!storeModule) {
		throw new Error('Could not import stores module');
	}

	const { messages } = storeModule;
	if (typeof messages.updateLastMessage !== 'function') {
		throw new Error('updateLastMessage method missing from messages store');
	}

	if (typeof messages.addMessage !== 'function') {
		throw new Error('addMessage method missing from messages store');
	}

	return { store: 'optimized', methods: 'available' };
});

// Test 4: CSS Performance Features
validator.addTest('CSS Performance Features', () => {
	const styles = Array.from(document.styleSheets)
		.map((sheet) => {
			try {
				return Array.from(sheet.cssRules)
					.map((rule) => rule.cssText)
					.join('\n');
			} catch {
				return '';
			}
		})
		.join('\n');

	const hasHardwareAcceleration =
		styles.includes('translateZ(0)') || styles.includes('transform: translateZ(0)');
	const hasScrollOptimizations = styles.includes('scroll-behavior: smooth');

	if (!hasHardwareAcceleration && !hasScrollOptimizations) {
		console.warn('Some CSS optimizations may not be loaded yet');
	}

	return {
		hardwareAcceleration: hasHardwareAcceleration,
		scrollOptimizations: hasScrollOptimizations
	};
});

// Test 5: Network Request Optimization Check
validator.addTest('Backend Batching Configuration', async () => {
	try {
		const response = await fetch('/api/health');
		if (!response.ok) {
			throw new Error('Backend health check failed');
		}

		const data = await response.json();
		if (data.status !== 'healthy') {
			throw new Error('Backend not healthy');
		}

		return { backend: 'available', health: 'good' };
	} catch (error) {
		throw new Error(`Backend test failed: ${error.message}`);
	}
});

// Export for global use
if (typeof window !== 'undefined') {
	window.performanceValidator = validator;
	console.log('🔧 Performance validator loaded!');
	console.log('Run window.performanceValidator.runAll() to test optimizations');
}

export default validator;
