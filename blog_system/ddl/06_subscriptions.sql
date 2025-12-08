-- Таблица подписок
CREATE TABLE IF NOT EXISTS subscriptions (
    subscriber_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscribed_to_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (subscriber_id, subscribed_to_id),
    CHECK (subscriber_id != subscribed_to_id)
);

CREATE INDEX idx_subscriptions_subscriber ON subscriptions(subscriber_id);
CREATE INDEX idx_subscriptions_subscribed_to ON subscriptions(subscribed_to_id);