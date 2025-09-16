# Pankitchen アプリケーション

## プロジェクト概要

Pankitchen は、パン作りが好きな人々が集まり、自身の作品を投稿・共有し、レシピやノウハウを交換するコミュニティアプリです。

## 環境構築

### 必要なツール

*   **Docker**: バックエンドのデータベース、キャッシュ、APIサーバーをコンテナで実行するために必要です。
*   **Node.js & npm (または yarn)**: フロントエンドの依存関係管理とビルドに必要です。

### セットアップ手順

1.  **プロジェクトのクローン**

    ```bash
    git clone <リポジトリのURL>
    cd Pankitchen
    ```

2.  **バックエンドのセットアップと起動**

    プロジェクトのルートディレクトリ (`Pankitchen`) で以下のコマンドを実行します。

    ```bash
    # Dockerコンテナのビルドと起動
    docker-compose build
    docker-compose up -d
    ```

    *   初回起動時は、Pythonの依存関係のインストールやDockerイメージのダウンロードに時間がかかる場合があります。
    *   PostgreSQLのポート `5432` が既にローカルで使用されている場合、`docker-compose.yml` の `db` サービス内の `ports` を `"5433:5432"` のように変更してください。

3.  **フロントエンドのセットアップ**

    フロントエンドのディレクトリ (`Pankitchen/frontend/PankitchenFrontend`) に移動し、依存関係をインストールします。

    ```bash
    cd frontend/PankitchenFrontend
    npm install
    ```

## アプリケーションの起動方法

### バックエンド (APIサーバー)

バックエンドは Docker Compose で起動されているため、通常は追加の操作は不要です。バックグラウンドで実行されています。

*   **APIドキュメント (Swagger UI)**: `http://localhost:8000/docs` にアクセスすると、APIのエンドポイントを確認できます。

### フロントエンド (Expo アプリ)

フロントエンドのディレクトリ (`Pankitchen/frontend/PankitchenFrontend`) で以下のコマンドを実行します。

*   **Web版を起動**:

    ```bash
    npm run web
    ```

    ブラウザが自動的に開き、アプリケーションが表示されます。

*   **Android版を起動**:

    ```bash
    npm run android
    ```

    Androidエミュレータまたは接続されたデバイスでアプリケーションが起動します。

## 開発について

### バックエンド

*   コードを変更した場合、Dockerコンテナを再起動する必要がある場合があります。
    ```bash
    docker-compose restart backend
    ```

### フロントエンド

*   コードを変更すると、開発サーバーが自動的にリロードされます。
*   Web版で `localhost` へのAPIリクエストがうまくいかない場合、AndroidエミュレータからホストPCのバックエンドにアクセスするには、`frontend/PankitchenFrontend/src/services/api.ts` の `baseURL` を `http://10.0.2.2:8000` に変更する必要があるかもしれません。
