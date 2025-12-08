# ER-диаграмма Blog System

```mermaid
erDiagram
    users {
        integer id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        text bio
        string profile_picture
        timestamp created_at
        timestamp updated_at
        boolean is_active
    }
    
    categories {
        integer id PK
        string name UK
        string slug UK
        text description
        timestamp created_at
    }
    
    posts {
        integer id PK
        integer user_id FK
        string title
        string slug
        text content
        text excerpt
        string status
        string featured_image
        timestamp created_at
        timestamp updated_at
        timestamp published_at
        integer view_count
    }
    
    comments {
        integer id PK
        integer post_id FK
        integer user_id FK
        integer parent_id FK
        text content
        timestamp created_at
        timestamp updated_at
        boolean is_deleted
    }
    
    favorites {
        integer user_id PK,FK
        integer post_id PK,FK
        timestamp created_at
    }
    
    subscriptions {
        integer subscriber_id PK,FK
        integer subscribed_to_id PK,FK
        timestamp created_at
    }
    
    post_categories {
        integer post_id PK,FK
        integer category_id PK,FK
    }
    
    users ||--o{ posts : "создает"
    users ||--o{ comments : "пишет"
    users ||--o{ favorites : "добавляет в избранное"
    users ||--o{ subscriptions : "подписывается"
    users ||--o{ subscriptions : "на него подписываются"
    
    posts ||--o{ comments : "имеет"
    posts ||--o{ favorites : "в избранном у"
    posts }o--o{ categories : "принадлежит к"
    
    comments ||--o{ comments : "является ответом на"