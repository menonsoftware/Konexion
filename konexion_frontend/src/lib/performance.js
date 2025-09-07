// Performance monitoring utilities for WebSocket streaming
class PerformanceMonitor {
	constructor() {
		this.metrics = {
			chunksReceived: 0,
			totalChunkTime: 0,
			uiUpdateTime: 0,
			messageCount: 0,
			lastChunkTime: 0,
			averageChunkDelay: 0
		};

		this.enabled = false; // Set to true for debugging
		this.observers = new Set();
	}

	enable() {
		this.enabled = true;
		console.log('Performance monitoring enabled');
	}

	disable() {
		this.enabled = false;
	}

	recordChunk(chunkSize, processingTime) {
		if (!this.enabled) return;

		this.metrics.chunksReceived++;
		this.metrics.totalChunkTime += processingTime;

		const now = performance.now();
		if (this.metrics.lastChunkTime > 0) {
			const delay = now - this.metrics.lastChunkTime;
			this.metrics.averageChunkDelay =
				(this.metrics.averageChunkDelay * (this.metrics.chunksReceived - 1) + delay) /
				this.metrics.chunksReceived;
		}
		this.metrics.lastChunkTime = now;

		this.notifyObservers('chunk', {
			size: chunkSize,
			processingTime,
			totalChunks: this.metrics.chunksReceived,
			averageDelay: this.metrics.averageChunkDelay
		});
	}

	recordUIUpdate(updateTime) {
		if (!this.enabled) return;

		this.metrics.uiUpdateTime += updateTime;
		this.notifyObservers('ui-update', { updateTime });
	}

	recordMessage() {
		if (!this.enabled) return;

		this.metrics.messageCount++;
		this.notifyObservers('message', { total: this.metrics.messageCount });
	}

	getMetrics() {
		return {
			...this.metrics,
			averageChunkProcessingTime:
				this.metrics.chunksReceived > 0
					? this.metrics.totalChunkTime / this.metrics.chunksReceived
					: 0,
			averageUIUpdateTime:
				this.metrics.messageCount > 0 ? this.metrics.uiUpdateTime / this.metrics.messageCount : 0
		};
	}

	reset() {
		this.metrics = {
			chunksReceived: 0,
			totalChunkTime: 0,
			uiUpdateTime: 0,
			messageCount: 0,
			lastChunkTime: 0,
			averageChunkDelay: 0
		};
		console.log('Performance metrics reset');
	}

	subscribe(callback) {
		this.observers.add(callback);
		return () => this.observers.delete(callback);
	}

	notifyObservers(event, data) {
		this.observers.forEach((callback) => {
			try {
				callback(event, data);
			} catch (error) {
				console.error('Performance monitor callback error:', error);
			}
		});
	}

	logSummary() {
		if (!this.enabled) return;

		const metrics = this.getMetrics();
		console.group('📊 Performance Summary');
		console.log('Chunks received:', metrics.chunksReceived);
		console.log(
			'Average chunk processing time:',
			metrics.averageChunkProcessingTime.toFixed(2) + 'ms'
		);
		console.log('Average chunk delay:', metrics.averageChunkDelay.toFixed(2) + 'ms');
		console.log('Messages processed:', metrics.messageCount);
		console.log('Average UI update time:', metrics.averageUIUpdateTime.toFixed(2) + 'ms');
		console.groupEnd();
	}
}

// Create global instance
export const perfMonitor = new PerformanceMonitor();

// Development helper to enable monitoring
if (typeof window !== 'undefined' && import.meta.env.DEV) {
	window.perfMonitor = perfMonitor;
	console.log('Performance monitor available as window.perfMonitor');
	console.log('Use window.perfMonitor.enable() to start monitoring');
}

// Utilities for measuring performance
export function measureAsync(fn, label = '') {
	return async function (...args) {
		const start = performance.now();
		try {
			const result = await fn.apply(this, args);
			const end = performance.now();
			if (perfMonitor.enabled) {
				console.log(`⏱️ ${label} took ${(end - start).toFixed(2)}ms`);
			}
			return result;
		} catch (error) {
			const end = performance.now();
			if (perfMonitor.enabled) {
				console.error(`❌ ${label} failed after ${(end - start).toFixed(2)}ms`, error);
			}
			throw error;
		}
	};
}

export function measureSync(fn, label = '') {
	return function (...args) {
		const start = performance.now();
		try {
			const result = fn.apply(this, args);
			const end = performance.now();
			if (perfMonitor.enabled) {
				console.log(`⏱️ ${label} took ${(end - start).toFixed(2)}ms`);
			}
			return result;
		} catch (error) {
			const end = performance.now();
			if (perfMonitor.enabled) {
				console.error(`❌ ${label} failed after ${(end - start).toFixed(2)}ms`, error);
			}
			throw error;
		}
	};
}
